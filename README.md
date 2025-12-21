### Support
Those tests only have been tested on Mac and Linux (Ubuntu 24.04). Test automation may not work on other operating systems, but the tests can be launched manually (see Manual vs Auto Mode).

### Manual vs Auto Mode
Manual mode -> user copies prompts and pastes them into the chatbot manually
Auto mode -> prompts get copy-pasted into the chatbot automatically
Note: the goal of the Auto mode is to be able to run a full test suite without any intervention from the user. In practice, however, it may happen that the chatbox does not fully complete the task by itself (e.g.: a command hangs). It may be necessary to sometimes to nudge the chatbot to complete the task.

### Run all tests
To run all unit tests or all integration tests, use `launch_all_tests.py`

### Run one unit test
To run one unit test, use `launch_one_unit_test.py`

### Run one integration test
To run one integration test, use `launch_one_integration_test.py`

