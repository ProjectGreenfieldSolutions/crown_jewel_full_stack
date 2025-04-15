LOG_LEVEL = "INFO"
TEST_ENTRY_ACTIONS = ["combined_board_test", "paper_test"]
UNIVERSAL_ACTIONS = ["plants", "vendors", "customers", "corrugators", "paper_types", "grades", "flutes",
                     "order_test_codes", "special_instruction_codes"]
PROGRESS_ACTIONS = ["search_order", "find_rolls"] + ["find_" + action for action in UNIVERSAL_ACTIONS]
MYSQL_ACTIONS =  ["accounts", "lithos", "paper_test_reasons", "paper_test_positions", "paper_test_types",
                  "combined_board_test_reasons","combined_board_test_layers","combined_board_test_types"] + UNIVERSAL_ACTIONS + TEST_ENTRY_ACTIONS