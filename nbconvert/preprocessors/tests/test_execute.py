# coding=utf-8

"""
Module with tests for the execute preprocessor.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.
import os
import re
import nbformat

from ..execute import ExecutePreprocessor


addr_pat = re.compile(r'0x[0-9a-f]{7,9}')


def normalize_output(output):
    """
    Normalizes (most) outputs for comparison.
    """
    output = dict(output)
    if 'metadata' in output:
        del output['metadata']
    if 'text' in output:
        output['text'] = re.sub(addr_pat, '<HEXADDR>', output['text'])
    if 'text/plain' in output.get('data', {}):
        output['data']['text/plain'] = \
            re.sub(addr_pat, '<HEXADDR>', output['data']['text/plain'])
    for key, value in output.get('data', {}).items():
        if isinstance(value, str):
            output['data'][key] = value

    return output


def assert_notebooks_equal(expected, actual):
    expected_cells = expected['cells']
    actual_cells = actual['cells']
    assert len(expected_cells) == len(actual_cells)

    for expected_cell, actual_cell in zip(expected_cells, actual_cells):
        expected_outputs = expected_cell.get('outputs', [])
        actual_outputs = actual_cell.get('outputs', [])
        normalized_expected_outputs = list(map(normalize_output, expected_outputs))
        normalized_actual_outputs = list(map(normalize_output, actual_outputs))
        assert normalized_expected_outputs == normalized_actual_outputs

        expected_execution_count = expected_cell.get('execution_count', None)
        actual_execution_count = actual_cell.get('execution_count', None)
        assert expected_execution_count == actual_execution_count


def test_basic_execution():
    preprocessor = ExecutePreprocessor()
    fname = os.path.join(os.path.dirname(__file__), 'files', 'HelloWorld.ipynb')
    with open(fname) as f:
        input_nb = nbformat.read(f, 4)
        output_nb, _ = preprocessor.preprocess(input_nb)
    assert_notebooks_equal(input_nb, output_nb)


def test_populate_language_info():
    preprocessor = ExecutePreprocessor(kernel_name="python")
    nb = nbformat.v4.new_notebook()  # Certainly has no language_info.
    nb, _ = preprocessor.preprocess(nb, resources={})
    assert 'language_info' in nb.metadata  # See that a basic attribute is filled in
