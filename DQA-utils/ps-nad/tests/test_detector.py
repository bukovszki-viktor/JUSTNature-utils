import pytest
import pandas as pd
import numpy as np
from ps_nad.detector import PSNADetector

def test_detector_training():
    """Verify that the model trains and sets the is_trained flag."""
    data = pd.DataFrame({'val': np.random.normal(0, 1, 100)})
    detector = PSNADetector(contamination=0.1)
    detector.train(data, ['val'])
    assert detector.is_trained == True

def test_detector_prediction_shape():
    """Ensure the detector returns a series matching the input length."""
    data = pd.DataFrame({'val': np.random.normal(0, 1, 50)})
    detector = PSNADetector(contamination=0.1)
    detector.train(data, ['val'])
    predictions = detector.detect(data, ['val'])
    assert len(predictions) == 50
    assert set(predictions.unique()).issubset({1, -1})

def test_untrained_error():
    """Ensure calling detect before train raises a RuntimeError."""
    detector = PSNADetector()
    with pytest.raises(RuntimeError):
        detector.detect(pd.DataFrame({'val': [1]}), ['val'])