import numpy as np

from neuraxle.pipeline import Pipeline
from neuraxle.steps.util import PickleValueCachingWrapper, TransformCallbackStep, TapeCallbackFunction, \
    FitTransformCallbackStep

EXPECTED_OUTPUTS = [0.0, 0.0, 0.6931471805599453, 0.6931471805599453]


def test_transform_should_use_cache(tmpdir):
    tape_transform = TapeCallbackFunction()
    tape_fit = TapeCallbackFunction()
    p = Pipeline([
        PickleValueCachingWrapper(
            FitTransformCallbackStep(
                callback_function=tape_transform,
                fit_callback_function=tape_fit,
                transform_function=np.log),
            tmpdir
        )
    ])

    outputs = p.transform([1, 1, 2, 2])

    assert outputs == EXPECTED_OUTPUTS
    assert tape_transform.data == [[1], [2]]
    assert tape_fit.data == []


def test_fit_transform_should_fit_then_use_cache(tmpdir):
    tape_transform = TapeCallbackFunction()
    tape_fit = TapeCallbackFunction()
    p = Pipeline([
        PickleValueCachingWrapper(
            FitTransformCallbackStep(
                callback_function=tape_transform,
                fit_callback_function=tape_fit,
                transform_function=np.log),
            tmpdir
        )
    ])

    p, outputs = p.fit_transform([1, 1, 2, 2], [2, 2, 4, 4])

    assert outputs == EXPECTED_OUTPUTS
    assert tape_transform.data == [[1], [2]]
    assert tape_fit.data == [([1, 1, 2, 2], [2, 2, 4, 4])]


def test_should_flush_cache_on_every_fit(tmpdir):
    tape_transform = TapeCallbackFunction()
    tape_fit = TapeCallbackFunction()
    wrapper = PickleValueCachingWrapper(
        FitTransformCallbackStep(
            callback_function=tape_transform,
            fit_callback_function=tape_fit,
            transform_function=np.log),
        tmpdir
    )
    p = Pipeline([
        wrapper
    ])
    p.setup()
    wrapper.write_cache(1, 10)
    wrapper.write_cache(2, 20)

    p, outputs = p.fit_transform([1, 1, 2, 2], [2, 2, 4, 4])

    assert outputs == EXPECTED_OUTPUTS
    assert tape_transform.data == [[1], [2]]
    assert tape_fit.data == [([1, 1, 2, 2], [2, 2, 4, 4])]
