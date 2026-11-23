import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations, combinations_with_replacement


class RaceSimulator:
    """
    Simulates an F1 race strategy by calculating the time added
    from tire degradation and pit stops.
    """

    def __init__(self):
        """
        Initialize the simulator and store tire data.
        """

        self.tires = pd.DataFrame({
            'Tmin': [0,1,2],
            'Tmax': [10,10,10],
            'alpha': [0.5,0.25, 1/ 16],
            'beta': [15,25,55]
        }, index = ['Soft','Medium','Hard'])




    def tire_time(self, age, Tmin, Tmax, alpha, beta):
        """
        Calculate the time added due to tire degradation.

        Parameters:
            age: Tire age in laps.
            Tmin: Minimum time added by the tire.
            Tmax: Maximum time added by the tire.
            alpha: Tire degradation rate parameter.
            beta: Tire degradation midpoint parameter.

        Returns:
            Tire time added for the given tire age.
        """

        return Tmin + (Tmax - Tmin) / (1 + np.exp(-alpha * (age - beta)))


    def simulate(self, stint_lengths, tire_types):
        """
        Simulate a complete race strategy.

        Parameters:
            stint_lengths: Length of each race stint.
            tire_types: Tire compound used for each stint.

        Returns:
            Total time added from tire degradation and pit stops.
        """
        if len(stint_lengths) != 3 or len(tire_types) != 3:
            raise ValueError ("A race needs exactly three stints and three tire choices")
        if any(not isinstance(length, (int, np.integer)) or isinstance(length, (bool, np.bool_)) or length <= 0 for length in stint_lengths):
            raise ValueError("Stint lengths must be positive whole numbers.")
        if sum(stint_lengths) != 60:
            raise ValueError("Stint lengths must add up to 60 laps.")
        if len(set(tire_types)) < 2:
            raise ValueError("Use at least two different tire types.")
        if any(tire not in self.tires.index for tire in tire_types):
            raise ValueError("Unknown tire type. Use Soft, Medium, or Hard.")

        stints = []
        for stint_number, (length, tire) in enumerate(zip(stint_lengths, tire_types)):
            # New tires start at age zero, including on pit-stop laps.
            stint = pd.DataFrame({"age": np.arange(length)})
            params = self.tires.loc[tire]
            stint["tire_time"] = self.tire_time(
                stint["age"], params["Tmin"], params["Tmax"],
                params["alpha"], params["beta"]
            )
            stint["pit_time"] = 0
            if stint_number > 0:
                stint.loc[0, "pit_time"] = 25
            stints.append(stint)

        race = pd.concat(stints, ignore_index=True)
        return float((race["tire_time"] + race["pit_time"]).sum())

def plot_tires(simulator):
    """
    Plot tire degradation curves for all tire compounds.

    Parameters:
        simulator: A RaceSimulator object containing tire data.

    Returns:
        None.
    """
    pass


def plot_tires(simulator):
    """
    Plot tire degradation curves for all tire compounds.

    Parameters:
        simulator: A RaceSimulator object containing tire data.

    Returns:
        None.
    """
    ages = np.arange(60)
    plt.figure(figsize=(8, 6))
    for tire in simulator.tires.index:
        params = simulator.tires.loc[tire]
        times = simulator.tire_time(
            ages, params["Tmin"], params["Tmax"], params["alpha"], params["beta"]
        )
        plt.plot(ages, times, label=tire.lower())

    plt.xlabel("tire age (laps)")
    plt.ylabel("s/lap added")
    plt.legend()
    plt.show()


def find_best_strategy(simulator):
    """
    Test all valid race strategies and find the one
    with the minimum total time added.

    Parameters:
        simulator: A RaceSimulator object.

    Returns:
        A tuple containing (best_stint_lengths, best_tires, min_time).
    """
    best_time = float("inf")
    best_strategy = None

    # Pit stops occur on laps 2 through 60 (since stint 1 must be at least 1 lap)
    valid_pits = combinations(range(2, 61), 2)
    valid_tires = [
        t for t in combinations_with_replacement(simulator.tires.index, 3)
        if len(set(t)) >= 2
    ]

    for pit1, pit2 in valid_pits:
        stints = (pit1 - 1, pit2 - pit1, 61 - pit2)
        for tires in valid_tires:
            total_time = simulator.simulate(stints, tires)
            if total_time < best_time:
                best_time = total_time
                best_strategy = (stints, tires, total_time)

    return best_strategy
