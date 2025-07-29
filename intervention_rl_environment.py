# intervention_rl_environment.py

import gymnasium as gym
from gymnasium import spaces
from typing import Optional, List, Any, Dict
import numpy as np
from typing import Dict, Any, Tuple
from utils import logger
from database_utils import (
    db_manager,
)  # For fetching dynamic intervention types and student states


class StudentInterventionEnv(gym.Env):
    """
    A custom Gymnasium environment for simulating student academic progress
    and the impact of interventions.

    The environment models the student's longitudinal academic journey,
    incorporating their evolving state based on predicted marks, attendance,
    and a wide array of contextual features. Actions (interventions) are
    dynamically defined via database tables.
    """

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(
        self,
        student_id: str,
        initial_state: Dict[str, Any],
        render_mode: Optional[str] = None,
    ):
        super().__init__()
        self.student_id = student_id
        self._current_state = initial_state
        self.render_mode = render_mode

        # Dynamically load intervention types and their potential effects from the database
        self.intervention_types = self._load_intervention_types()
        if not self.intervention_types:
            logger.error(
                "No intervention types loaded. RL environment cannot function."
            )
            raise ValueError("Intervention types not loaded from database.")

        self.num_interventions = len(self.intervention_types)

        # Define action space: Each action corresponds to an intervention type
        # Or a combination of interventions, depending on complexity.
        # For simplicity, let's say each action is selecting one intervention.
        self.action_space = spaces.Discrete(
            self.num_interventions
        )  # N possible interventions

        # Define observation space: This should represent the student's state.
        # This will be a flattened representation of relevant student features.
        # Example features: current_mark, attendance_percentage, home_env_encoded, etc.
        # The size of this space depends heavily on the preprocessed features.
        # For demonstration, let's assume a fixed size for now based on a few key features.
        # In a real scenario, this would be derived from the output of DataPreprocessor.

        # Example observation space (adjust based on actual preprocessed features)
        # Assuming features like: current_mark, attendance, home_env_score, internet_access_score, study_habits_score
        self.observation_space = spaces.Box(
            low=0, high=100, shape=(5,), dtype=np.float32
        )  # Example: mark, attendance, 3 encoded features

        # Internal state for rendering (if needed)
        self.window = None
        self.clock = None

        logger.info(f"StudentInterventionEnv initialized for student {student_id}.")

    def _load_intervention_types(self) -> List[Dict[str, Any]]:
        """
        Loads intervention types and their properties (e.g., cost, potential impact)
        from the 'intervention_type_lookup' table.
        """
        logger.info("Loading intervention types from database.")
        # Example query to fetch intervention types
        query = "SELECT id, name, description, potential_impact_score, cost FROM intervention_type_lookup;"
        interventions = db_manager.execute_query(query)
        if not interventions:
            logger.warning("intervention_type_lookup table is empty or not found.")
        return interventions

    def _get_obs(self) -> np.ndarray:
        """
        Converts the current student state dictionary into a numerical observation
        array for the RL agent.
        This needs to align with the `observation_space` definition.
        """
        # This is a highly simplified mapping. In reality, you'd use the
        # DataPreprocessor to convert self._current_state into a feature vector.
        # For now, let's assume _current_state has these keys:
        # 'current_mark', 'attendance_percentage', 'home_env_encoded', 'internet_access_encoded', 'study_habits_encoded'

        # Ensure the values are within the observation space bounds
        current_mark = self._current_state.get("current_mark", 50.0)
        attendance_percentage = self._current_state.get("attendance_percentage", 70.0)
        home_env_encoded = self._current_state.get("home_env_encoded", 0)
        internet_access_encoded = self._current_state.get("internet_access_encoded", 0)
        study_habits_encoded = self._current_state.get("study_habits_encoded", 0)

        # Normalize or scale values if observation space is defined with specific ranges
        obs = np.array(
            [
                current_mark,
                attendance_percentage,
                float(home_env_encoded),
                float(internet_access_encoded),
                float(study_habits_encoded),
            ],
            dtype=np.float32,
        )
        return obs

    def _get_info(self) -> Dict[str, Any]:
        """Provides auxiliary information for debugging or logging."""
        return {
            "student_id": self.student_id,
            "current_mark": self._current_state.get("current_mark"),
        }

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Resets the environment to an initial state.
        This typically involves fetching the student's initial state from the database.
        """
        super().reset(seed=seed)

        # Fetch initial student state from database (or use the one passed in init)
        # In a real scenario, this would query the Students table and relevant lookups
        # to get the initial features for a student.
        # For now, we use the initial_state provided during __init__.
        # If options contains a new student_id, you could fetch that here.

        observation = self._get_obs()
        info = self._get_info()

        logger.info(
            f"Environment reset for student {self.student_id}. Initial mark: {self._current_state.get('current_mark')}"
        )
        return observation, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Applies an action (intervention) to the environment and calculates
        the next state, reward, and termination status.
        """
        intervention_applied = self.intervention_types[action]
        logger.info(
            f"Applying intervention: {intervention_applied['name']} for student {self.student_id}"
        )

        # Simulate the effect of the intervention on the student's state.
        # This is where the core logic of the RL environment resides.
        # The 'potential_impact_score' from the database can be used here.

        # Example: Intervention increases the mark, but with some randomness
        impact = (
            intervention_applied.get("potential_impact_score", 0) / 10.0
        )  # Scale impact

        # Simulate a change in current mark
        old_mark = self._current_state.get("current_mark", 50.0)
        new_mark = old_mark + impact + np.random.uniform(-5, 5)  # Add some noise
        new_mark = np.clip(new_mark, 0, 100)  # Keep mark within 0-100 bounds
        self._current_state["current_mark"] = new_mark

        # Reward calculation: Higher mark is better, but cost of intervention is negative.
        # Cost would also come from the database.
        intervention_cost = intervention_applied.get("cost", 1.0)
        reward = (new_mark - old_mark) - (
            intervention_cost * 0.1
        )  # Example reward function

        # Determine if the episode is terminated (e.g., student reaches target mark, or drops out)
        terminated = (
            new_mark >= 80 or self._current_state.get("dropout_risk", 0.0) > 0.8
        )  # Example termination
        truncated = False  # For now, no truncation based on time limits

        observation = self._get_obs()
        info = self._get_info()

        logger.info(
            f"Step result: New mark={new_mark:.2f}, Reward={reward:.2f}, Terminated={terminated}"
        )
        return observation, reward, terminated, truncated, info

    def render(self) -> None:
        """Renders the environment (optional, for visualization)."""
        if self.render_mode == "human":
            logger.debug("Rendering environment (placeholder).")
            # Implement visual rendering if needed, e.g., using Pygame or Matplotlib
            pass

    def close(self) -> None:
        """Cleans up resources (e.g., close render window)."""
        logger.info("Closing environment.")
        if self.window is not None:
            self.window.close()
            self.window = None


# Example Usage:
if __name__ == "__main__":
    # Ensure db_manager is connected for this test
    try:
        db_manager.connect()
        # Create a dummy intervention_type_lookup table if it doesn't exist
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'intervention_type_lookup')
            CREATE TABLE intervention_type_lookup (id INT PRIMARY KEY, name NVARCHAR(100), description NVARCHAR(255), potential_impact_score FLOAT, cost FLOAT);
        """
        )
        db_manager.execute_non_query(
            "INSERT INTO intervention_type_lookup (id, name, description, potential_impact_score, cost) VALUES (0, 'Tutoring', 'One-on-one academic support', 7.5, 5.0) WHERE NOT EXISTS (SELECT 1 FROM intervention_type_lookup WHERE id = 0);"
        )
        db_manager.execute_non_query(
            "INSERT INTO intervention_type_lookup (id, name, description, potential_impact_score, cost) VALUES (1, 'Mentorship', 'Guidance from a mentor', 5.0, 2.0) WHERE NOT EXISTS (SELECT 1 FROM intervention_type_lookup WHERE id = 1);"
        )
        db_manager.execute_non_query(
            "INSERT INTO intervention_type_lookup (id, name, description, potential_impact_score, cost) VALUES (2, 'Counseling', 'Emotional support', 6.0, 3.0) WHERE NOT EXISTS (SELECT 1 FROM intervention_type_lookup WHERE id = 2);"
        )

        initial_student_state = {
            "student_id": "S001",
            "current_mark": 60.0,
            "attendance_percentage": 85.0,
            "home_env_encoded": 1,
            "internet_access_encoded": 0,
            "study_habits_encoded": 1,
            "dropout_risk": 0.1,
        }

        env = StudentInterventionEnv(
            student_id="S001", initial_state=initial_student_state
        )

        obs, info = env.reset()
        print(f"Initial Observation: {obs}, Info: {info}")

        # Simulate a few steps
        total_reward = 0
        for i in range(3):
            action = env.action_space.sample()  # Randomly choose an intervention
            print(f"\nStep {i+1}: Taking action {action}")
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            print(
                f"  Obs: {obs}, Reward: {reward:.2f}, Terminated: {terminated}, Info: {info}"
            )
            if terminated:
                print("Episode terminated.")
                break

        print(f"\nTotal Reward: {total_reward:.2f}")
        env.close()

    except Exception as e:
        logger.error(f"An error occurred during intervention_rl_environment test: {e}")
    finally:
        db_manager.close()
