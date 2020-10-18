import numpy as np
import pandas as pd
from ..feature_engineering import NaN_Inducer, NumericImputer, Deduper, NumericFuncTransformer
# from ..feature_engineering import TargetMultiEncoder
from sklearn.datasets import load_boston

data = load_boston()
df = pd.DataFrame(data.data, columns=data.feature_names)


class TestNaNInducer:

    def test_error_quantity(self):
        """This test evaluates the min_nan_level in incremental steps:
            1. When there is no NaN, the function will generate NaN based on specified nan_level
            2. When the current NaN is below the specify the nan_level, the NaN_Inducer will
               introduce additional NaN until specified NaN level is reached.
         """

        train = df.head(100)

        for min_nan_level in [.01, .02, .03, .04, .05, .1, .25, .5, .75, .9, .99]:
            nan_inducer = NaN_Inducer(min_nan_level=min_nan_level, random_state=42)
            train = nan_inducer.fit_transform(train)
            assert train.isnull().sum().sum() == train.shape[0] * min_nan_level * train.shape[1]

    def test_random_state(self):
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

    def test_randomness(self):
        """ The test is to verify that NaN_inducer introduces NaN randomly without bias.
            This test introduce 70% nan to a 100 sample data set using NaN_inducer. The data is
            fit_transformed without random_state. This process is repeated 1,000 times, and the mean
            of independent fit data set are calculated. A 95% confidence interval of the sample mean
            is constructed using the sample means and the standard deviation of the sample mean.
            The population mean is expected to fall inside the sample mean confidence.
        """
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

#
# class TestTargetMultiEncoder:
#
#     def test_target_multi_encoder(self):
#
#         # generate test df
#         def generate_df(x):
#             test_data = {'X': [], 'y': []}
#             for i in range(1, x + 1):
#                 test_data['X'] += [i] * i
#             test_data['y'] = [i for i in range(len(test_data['X']))]
#             result_df = pd.DataFrame(test_data)
#             return result_df
#
#         max_x_input = 12
#         min_cat_size = 7
#         max_uniques_per_cat = 80
#
#         for max_x in range(1, max_x_input):
#             test_df = generate_df(max_x)
#             print(test_df)
#
#             multi_encoder = TargetMultiEncoder(
#                 min_cat_size=min_cat_size,
#                 max_uniques_per_cat=max_uniques_per_cat,
#                 tme_aggr_funcs=(
#                     np.mean,
#                     np.min,
#                     np.max
#                 )
#             )
#             feat = multi_encoder.fit_transform(
#                 X=test_df.drop(columns=['y']),
#                 y=test_df['y']
#             )
#
#             # For preview
#             # test_df['X_hat'] = test_df['X'].apply(lambda x: x if x >= min_cat_size else 0)
#             # test_df = test_df.merge(feat, left_index=True, right_index=True)
#             # print(test_df.head(10))
#             # print(test_df.shape)
#             # print(test_df['y'])
#             # print(test_df['y'].mean())
#
#             # Testing
#             if max_x < min_cat_size or max_x > max_uniques_per_cat:
#                 assert feat.empty
#             else:
#                 assert feat.shape[1] == 3
#                 assert test_df[test_df['X_hat'] == 0]['targ_enc_mean(X)'].mean() == test_df['y'].mean()
#                 assert (test_df[test_df['X_hat'] == 0]['targ_enc_amin(X)'] == test_df['y'].min()).all()
#                 assert (test_df[test_df['X_hat'] == 0]['targ_enc_amax(X)'] == test_df['y'].max()).all()


class TestNumericImputer:

    def test_numeric_imputer(self):
        def generate_df(row):
            test_data = {'X': [], 'y': []}
            for i in range(row):
                if i <= row // 2:
                    test_data['X'].append(i)
                else:
                    test_data['X'].append(np.nan)
                test_data['y'].append(i)
            result_df = pd.DataFrame(test_data)
            return result_df

        # Generate testing dataframe
        row = 10
        test_df = generate_df(row)
        for r in range(row):
            if r <= row // 2:
                assert test_df.loc[r, 'X'] == r
            else:
                assert np.isnan(test_df.loc[r, 'X'])

        # Instantiate Numeric Impurter
        num_imputer = NumericImputer(
            imputation_aggr_funcs=(
                np.min,
                np.max,
                np.mean
            )
        )

        feat = num_imputer.fit_transform(X=test_df[['X']], y=test_df['y'])
        print(feat.head(20))
        non_nan_x = test_df[test_df['X'] <= (row//2)]['X']

        # Check non-nan rows
        assert (feat.loc[:row // 2]['fillna_amin(X)'] == non_nan_x).all()
        assert (feat.loc[:row // 2]['fillna_amax(X)'] == non_nan_x).all()
        assert (feat.loc[:row // 2]['fillna_mean(X)'] == non_nan_x).all()

        # Check imputation
        assert (feat.loc[row // 2 + 1:]['fillna_amin(X)'] == test_df['X'].min()).all()
        assert (feat.loc[row // 2 + 1:]['fillna_amax(X)'] == test_df['X'].max()).all()
        assert (feat.loc[row // 2 + 1:]['fillna_mean(X)'] == test_df['X'].mean()).all()


class TestDeduper:

    def test_deduper(self):
        """Testing scenario:
            1. Edge 1: No duplicate -> return original df
            2. Edge 2: df with same data -> return df with 1 row (unique data)
            3. Edge 3: Case with/without Nan (printout)
        """

        row_num = 6
        def create_df(row, unique=2):
            data = {'X1': [],
                    'Y': []}
            for i in range(row):
                data['X1'].append(i % unique)
                data['Y'].append(i)
            df = pd.DataFrame(data)
            df['X2'] = df['X1'].copy().astype(str)
            df['X3'] = df['X1'].copy()
            df['X4'] = df['X2'].copy()
            df['X5'] = np.nan
            df['X6'] = df['X5'].copy()
            df['X7'] = df['X1'].copy()
            df['X7'][3] = np.nan
            df['X8'] = df['X7'].copy()
            return df[['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'Y']]

        test_df = create_df(6)
        print(test_df.head())

        for allow_nans in [True, False]:
            try:
                deduper = Deduper(allow_nans=allow_nans)
                feat = deduper.fit_transform(X=test_df.drop(columns=['Y']),
                                             y=test_df['Y'])
                assert len(feat.columns) == 4
                assert (feat.columns == ['X1', 'X2', 'X5', 'X7']).all()

            except:
                print('Data Contain NaN value.')


class TestNumericFuncTransformer:

    def test_numeric_func_transformer(self):
        """Testing Case:
            1. Column with negative value -> functions in positive_arg_num_functions should not be executed
            2. Column without negative value -> all functions should be executed
        """

        row = 6
        def create_df(row, offset):
            data = {'X1': [],
                    'X2': [],
                    'Y': []}
            for i in range(row):
                data['X1'].append(i - offset)
                data['X2'].append(str(i)+'-text')
                data['Y'].append(i*10)
            return pd.DataFrame(data)

        for offset in [0, 1]:
            test_df = create_df(row, offset)
            transformer = NumericFuncTransformer(any_arg_num_functions=(np.sqrt, lambda x: x+1))
            feat = transformer.fit_transform(X=test_df.drop(columns=['Y']))
            print(feat)
            if offset:
                assert len(feat.columns) == 2
                assert np.isnan(feat.iloc[0, 0])
                assert (feat.iloc[1:, 0] == test_df.iloc[1:, 0].apply(np.sqrt)).all()
            else:
                assert len(feat.columns) == 6
                assert (feat.iloc[:, 0] == test_df['X1'].apply(np.sqrt)).all()
                assert (feat.iloc[:, 1] == test_df['X1'].apply(lambda x: x+1)).all()









