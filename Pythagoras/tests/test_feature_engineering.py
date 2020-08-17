import numpy as np
import pandas as pd
from ..feature_engineering import NaN_Inducer
from sklearn.datasets import load_boston

data = load_boston()
df = pd.DataFrame(data.data, columns=data.feature_names)


def test_NaN_Inducer_error_quantity():
    train = df.head(100)

    for min_nan_level in [.01, .02, .03, .04, .05, .1, .25, .5, .75, .9, .99]:
        """This test the min_nan_level in increamental steps:
           1. When there is no NaN, the function will generate NaN based on specified nan_level
           2. When the current NaN is below the specify the nan_level, the NaN_Inducer will 
              add NaN to the specified level.
        """
        nan_inducer = NaN_Inducer(min_nan_level=min_nan_level, random_state=42)
        train = nan_inducer.fit_transform(train)
        assert train.isnull().sum().sum() == train.shape[0] * min_nan_level * train.shape[1]


def test_NaN_Inducer_random_state():
    """Two test cases for 5 fit_transforms:
       1. With random state: NaN_inducer is expected to generate the same random NaN. The feature mean
          from the ten independent fit_trainsform should be the same (NaNs are induced to the same locations).
       2. Without random state: The feature mean from the ten independent fit_trainsform should be different
          (NaNs are induced to different locations).
    """
    output_means = []

    # With Random_state: Expect the mean to be the same
    for _ in range(10):
        nan_inducer = NaN_Inducer(min_nan_level=.5, random_state=42)
        train = df.head(100)
        train = nan_inducer.fit_transform(train)
        output_means.append(train.mean()[0])

    for i in range(len(output_means) - 1):
        assert output_means[i] == output_means[i + 1]

    # Without Random_state: Expect the mean to be different
    output_means = []
    for _ in range(10):
        nan_inducer = NaN_Inducer(min_nan_level=.5, random_state=None)
        train = df.head(100)
        train = nan_inducer.fit_transform(train)
        output_means.append(train.mean()[0])

    for i in range(len(output_means) - 1):
        assert output_means[i] != output_means[i + 1]


def test_NaN_Inducer_randomness():
    ''' The test is to verify the induction of nan is truly random without bias.
        This test introduce 70% nan of a 100 sample data set 1000 times (simulation).
        The data is fit_transformed without random_state. A 95% confidence interval of the
        sample mean is constructed. The population mean is expected to fall inside the
        sample mean confidence. 
    '''
    train = df.head(100)
    pop_mean = train.mean()[0]
    sample_mean = []
    for _ in range(1000):
        nan_inducer = NaN_Inducer(min_nan_level=.7, random_state=None)
        sample = nan_inducer.fit_transform(train)
        sample_mean.append(sample.mean()[0])
    mean_sample_mean = np.mean(sample_mean)
    std_sample_mean = np.std(sample_mean)
    confidence_interval_95 = [
        mean_sample_mean - 1.96 * std_sample_mean,
        mean_sample_mean + 1.96 * std_sample_mean
    ]
    assert min(confidence_interval_95) <= pop_mean <= max(confidence_interval_95)






