# intervention_rl_agent.py

from stable_baselines3 import PPO, A2C
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback
import os
from typing import Dict, Any, Optional
from utils import logger
from intervention_rl_environment import StudentInterventionEnv
from database_utils import (
    db_manager,
)  # For fetching student data for env initialization


class RLInterventionAgent:
    """
    Trains and manages a Reinforcement Learning agent to recommend
    optimal student interventions using Stable Baselines3.
    """

    def __init__(
        self,
        model_type: str = "PPO",
        log_dir: str = "rl_logs",
        model_save_path: str = "rl_models",
    ):
        self.model_type = model_type
        self.log_dir = log_dir
        self.model_save_path = model_save_path
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.model_save_path, exist_ok=True)
        self.model = None

    def _get_initial_student_state(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the initial state for a student from the database
        to initialize the RL environment.
        This would involve a comprehensive query similar to prediction_service.
        """
        logger.info(
            f"Fetching initial state for student {student_id} for RL environment."
        )
        # Example query:
        # query = f"""
        # SELECT
        #     s.student_id, s.current_mark, s.attendance_percentage,
        #     hle.id AS home_env_encoded, ia.id AS internet_access_encoded, sh.id AS study_habits_encoded,
        #     s.dropout_risk -- Assuming dropout_risk is directly in Students table or derived
        # FROM
        #     Students s
        # LEFT JOIN home_learning_environment_lookup hle ON s.home_learning_environment_id = hle.id
        # LEFT JOIN internet_access_lookup ia ON s.internet_access_id = ia.id
        # LEFT JOIN study_habits_lookup sh ON s.study_habits_id = sh.id
        # WHERE s.student_id = ?;
        # """
        # state_data = db_manager.execute_query(query, (student_id,))

        # Simulate initial state data for demonstration
        if student_id == "S001":
            return {
                "student_id": "S001",
                "current_mark": 60.0,
                "attendance_percentage": 85.0,
                "home_env_encoded": 1,  # Example encoded values
                "internet_access_encoded": 0,
                "study_habits_encoded": 1,
                "dropout_risk": 0.1,
            }
        else:
            logger.warning(f"Initial state not found for student {student_id}.")
            return None

    def train_agent(self, student_id: str, total_timesteps: int = 10000) -> None:
        """
        Trains the RL agent for a specific student.
        """
        initial_state = self._get_initial_student_state(student_id)
        if not initial_state:
            logger.error(
                f"Cannot train agent for student {student_id}: initial state not found."
            )
            return

        # Create the environment for training
        # Using a lambda function to pass initial_state to the environment constructor
        env = make_vec_env(
            lambda: StudentInterventionEnv(student_id, initial_state), n_envs=1
        )

        # Define the model based on model_type
        if self.model_type == "PPO":
            self.model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=self.log_dir)
        elif self.model_type == "A2C":
            self.model = A2C("MlpPolicy", env, verbose=1, tensorboard_log=self.log_dir)
        else:
            logger.error(f"Unsupported RL model type: {self.model_type}")
            return

        # Setup evaluation callback to save the best model
        eval_env = StudentInterventionEnv(
            student_id, initial_state
        )  # Separate env for evaluation
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=self.model_save_path,
            log_path=self.log_dir,
            eval_freq=1000,
            deterministic=True,
            render_freq=0,
        )

        logger.info(
            f"Starting training for {self.model_type} agent for student {student_id}..."
        )
        self.model.learn(total_timesteps=total_timesteps, callback=eval_callback)
        self.model.save(
            os.path.join(self.model_save_path, f"{self.model_type}_{student_id}_final")
        )
        logger.info(f"Training complete. Model saved to {self.model_save_path}.")
        env.close()
        eval_env.close()

    def load_agent(self, student_id: str) -> bool:
        """
        Loads a trained RL agent for a specific student.
        """
        model_filepath = os.path.join(
            self.model_save_path, f"{self.model_type}_{student_id}_final.zip"
        )
        if not os.path.exists(model_filepath):
            logger.error(
                f"RL agent model not found for student {student_id} at {model_filepath}"
            )
            return False

        try:
            if self.model_type == "PPO":
                self.model = PPO.load(model_filepath)
            elif self.model_type == "A2C":
                self.model = A2C.load(model_filepath)
            logger.info(
                f"Successfully loaded {self.model_type} agent for student {student_id}."
            )
            return True
        except Exception as e:
            logger.error(
                f"Error loading RL agent model from {model_filepath}: {e}",
                exc_info=True,
            )
            return False

    def recommend_intervention(self, student_id: str) -> Optional[int]:
        """
        Uses the loaded RL agent to recommend an intervention for the student.
        """
        if self.model is None:
            if not self.load_agent(student_id):
                logger.error(
                    f"Cannot recommend intervention for student {student_id}: agent not loaded."
                )
                return None

        initial_state = self._get_initial_student_state(student_id)
        if not initial_state:
            logger.error(
                f"Cannot recommend intervention for student {student_id}: current state not found."
            )
            return None

        # Create a temporary environment to get the observation space for prediction
        temp_env = StudentInterventionEnv(student_id, initial_state)
        obs, _ = temp_env.reset()
        temp_env.close()  # Close immediately after getting observation

        try:
            action, _states = self.model.predict(obs, deterministic=True)
            logger.info(
                f"Recommended action (intervention ID) for student {student_id}: {action}"
            )
            return int(action)
        except Exception as e:
            logger.error(
                f"Error recommending intervention for student {student_id}: {e}",
                exc_info=True,
            )
            return None


# Example Usage:
if __name__ == "__main__":
    # Ensure db_manager is connected for this test
    try:
        db_manager.connect()
        # Ensure dummy intervention_type_lookup table is created
        # (as done in intervention_rl_environment.py __main__ block)

        rl_agent = RLInterventionAgent(model_type="PPO")

        test_student_id = "S001"

        # Train the agent (this can take some time)
        logger.info(f"\n--- Starting RL Agent Training for {test_student_id} ---")
        rl_agent.train_agent(
            test_student_id, total_timesteps=1000
        )  # Reduced timesteps for quick test
        logger.info(f"--- RL Agent Training for {test_student_id} Completed ---")

        # Load the trained agent
        if rl_agent.load_agent(test_student_id):
            # Recommend an intervention
            recommended_action = rl_agent.recommend_intervention(test_student_id)
            if recommended_action is not None:
                print(
                    f"\nRecommended intervention ID for {test_student_id}: {recommended_action}"
                )
            else:
                print(f"\nFailed to recommend intervention for {test_student_id}.")
        else:
            print(f"\nFailed to load RL agent for {test_student_id}.")

    except Exception as e:
        logger.error(f"An error occurred during intervention_rl_agent test: {e}")
    finally:
        db_manager.close()
