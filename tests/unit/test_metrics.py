#!/usr/bin/env python3
"""
Unit tests for metrics collection functionality.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.metrics import (
    setup_metrics,
    get_metric,
    METRICS,
    increment_counter, 
    observe_latency,
    set_gauge
)

class TestMetrics(unittest.TestCase):
    """Tests for the metrics collection module."""
    
    @patch('prometheus_client.Counter')
    @patch('prometheus_client.Gauge')
    @patch('prometheus_client.Histogram')
    @patch('prometheus_client.start_http_server')
    def test_setup_metrics(self, mock_start_server, mock_histogram, mock_gauge, mock_counter):
        """Test that metrics setup correctly initializes all metrics."""
        # Setup mocks
        mock_counter.return_value = MagicMock()
        mock_gauge.return_value = MagicMock()
        mock_histogram.return_value = MagicMock()
        
        # Call setup metrics
        setup_metrics(port=9090)
        
        # Assertions
        mock_start_server.assert_called_once_with(9090)
        
        # Should have created metrics for each type in METRICS
        counter_calls = 0
        gauge_calls = 0
        histogram_calls = 0
        
        for metric_type, metrics in METRICS.items():
            if metric_type == "counter":
                counter_calls += len(metrics)
            elif metric_type == "gauge":
                gauge_calls += len(metrics)
            elif metric_type == "histogram":
                histogram_calls += len(metrics)
        
        self.assertEqual(mock_counter.call_count, counter_calls)
        self.assertEqual(mock_gauge.call_count, gauge_calls)
        self.assertEqual(mock_histogram.call_count, histogram_calls)
    
    @patch('src.utils.metrics._metrics')
    def test_get_metric(self, mock_metrics):
        """Test that get_metric returns the correct metric."""
        # Setup mock
        mock_metrics.return_value = {"counter": {"test_counter": "counter_obj"}}
        
        # Call function
        result = get_metric("counter", "test_counter")
        
        # Assert
        self.assertEqual(result, "counter_obj")
    
    @patch('src.utils.metrics.get_metric')
    def test_increment_counter(self, mock_get_metric):
        """Test incrementing a counter."""
        # Setup mock
        mock_counter = MagicMock()
        mock_get_metric.return_value = mock_counter
        
        # Call function
        increment_counter("api_requests_total", labels={"endpoint": "/health"})
        
        # Assert
        mock_get_metric.assert_called_once_with("counter", "api_requests_total")
        mock_counter.labels.assert_called_once_with(endpoint="/health")
        mock_counter.labels.return_value.inc.assert_called_once_with(1)
    
    @patch('src.utils.metrics.get_metric')
    def test_set_gauge(self, mock_get_metric):
        """Test setting a gauge value."""
        # Setup mock
        mock_gauge = MagicMock()
        mock_get_metric.return_value = mock_gauge
        
        # Call function
        set_gauge("model_loaded", 1)
        
        # Assert
        mock_get_metric.assert_called_once_with("gauge", "model_loaded")
        mock_gauge.set.assert_called_once_with(1)
    
    @patch('src.utils.metrics.get_metric')
    @patch('src.utils.metrics.time.time')
    def test_observe_latency(self, mock_time, mock_get_metric):
        """Test observing request latency."""
        # Setup mock
        mock_histogram = MagicMock()
        mock_get_metric.return_value = mock_histogram
        mock_time.side_effect = [100, 100.5]  # Start time, end time
        
        # Use context manager
        with observe_latency("request_latency", labels={"endpoint": "/generate_playbook"}):
            pass
        
        # Assert
        mock_get_metric.assert_called_once_with("histogram", "request_latency")
        mock_histogram.labels.assert_called_once_with(endpoint="/generate_playbook")
        mock_histogram.labels.return_value.observe.assert_called_once_with(0.5)  # 100.5 - 100 = 0.5


if __name__ == "__main__":
    unittest.main()
