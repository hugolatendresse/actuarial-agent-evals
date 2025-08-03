benchmark = [
    {
        "id": "dummy_no_input",
        "source_exam": "",
        "source_year": "",
        "topics": [],
        "question_text": "Create a python script that outputs the following words in stdout: 'Sabrina eats chicken.'",
        "setup_code": "# Please write your Python code below",
        "verification": {
            "type": "text_output",
            "expected_output": "Sabrina eats chicken.",
            "evaluation_script": "assert expected in actual, f'Expected output to contain: {expected}, but got: {actual}'"
        }
    }
]