benchmark_cas = [
    {
        'question_id': 'EX5-F19-Q01',
        'domain': 'ratemaking',
        'topic': 'exposures',
        'question_text': {
            'prompt': 'Given the following quarterly exposure information and the notes provided, answer the following:',
            'type': 'multi_part',
            'parts': {
                'a': 'Calculate the 2017 policy year earned exposures as of March 31, 2018.',
                'b': 'Calculate the in-force exposures as of May 31, 2018.',
                'c': 'Calculate the calendar year 2018 unearned exposures.',
                'd': 'Calculate the calendar year 2019 quarter 1 earned exposures.'
            }
        },
        'inputs': [
            {
                'name': 'written_and_earned_exposures',
                'type': 'table',
                'data': [
                    {'quarter': '2017 Q1', 'written': 100, 'earned': 5.00},
                    {'quarter': '2017 Q2', 'written': 450, 'earned': 247.50},
                    {'quarter': '2017 Q3', 'written': 400, 'earned': 427.50},
                    {'quarter': '2017 Q4', 'written': 100, 'earned': 52.50},
                    {'quarter': '2018 Q1', 'written': 125, 'earned': 53.75},
                    {'quarter': '2018 Q2', 'written': 550, 'earned': 528.75},
                    {'quarter': '2018 Q3', 'written': 475, 'earned': 562.50},
                    {'quarter': '2018 Q4', 'written': 30, 'earned': 59.00}
                ]
            },
            {
                'name': 'notes',
                'type': 'notes',
                'data': 'The company started writing business on January 1, 2017. The company stopped writing business on December 31, 2018. The quarterly earnings pattern was set by analyzing historical experience across the industry and is not uniform. All policies are annual and written on the first day of the quarter. No policy cancellations or mid-term adjustments.'
            }
        ],
        'expected_answer': {
            'type': 'multi_part_numeric',
            'parts': {
                'a': {'value': 780.0, 'tolerance': 0.01},
                'b': {'value': 1175.0, 'tolerance': 0.01},
                'c': {'value': 293.5, 'tolerance': 0.01},
                'd': {'value': 52.75, 'tolerance': 0.01}
            }
        },
        'source': 'CAS Exam 5, Fall 2019, Question 1',
        'tags': [
            'written exposure',
            'earned exposure',
            'in-force exposure',
            'unearned exposure',
            'calendar year vs policy year'
        ]
    },
    
    {
        'question_id': 'EX5-F19-Q02',
        'domain': 'ratemaking',
        'topic': 'premiums',
        'question_text': {
            'prompt': 'Given the following policies for an insurance company:',
            'type': 'multi_part',
            'parts': {
                'a': 'Calculate the written premium for the fiscal year ending July 31, 2018.',
                'b': 'Calculate the in-force premium as of December 15, 2018.',
                'c': 'Calculate the 2018 calendar year written premium if Policy C is cancelled on March 31, 2018.'
            }
        },
        'inputs': [
            {
                'name': 'policies',
                'type': 'table',
                'data': [
                    {'policy': 'A', 'effective_date': '2017-03-01', 'expiration_date': '2018-02-28', 'written_premium': 1200},
                    {'policy': 'B', 'effective_date': '2017-06-01', 'expiration_date': '2017-11-30', 'written_premium': 1500},
                    {'policy': 'C', 'effective_date': '2017-07-01', 'expiration_date': '2018-06-30', 'written_premium': 2000},
                    {'policy': 'D', 'effective_date': '2017-10-01', 'expiration_date': '2018-09-30', 'written_premium': 750},
                    {'policy': 'E', 'effective_date': '2018-01-01', 'expiration_date': '2018-12-31', 'written_premium': 900},
                    {'policy': 'F', 'effective_date': '2018-04-01', 'expiration_date': '2018-09-30', 'written_premium': 1650},
                    {'policy': 'G', 'effective_date': '2018-08-01', 'expiration_date': '2019-07-31', 'written_premium': 1350}
                ]
            }
        ],
        'expected_answer': {
            'type': 'multi_part_numeric',
            'parts': {
                'a': {'value': 3300.0, 'tolerance': 0.01},
                'b': {'value': 2250.0, 'tolerance': 0.01},
                'c': {'value': 3400.0, 'tolerance': 0.01}
            }
        },
        'source': 'CAS Exam 5, Fall 2019, Question 2',
        'tags': [
            'written premium',
            'fiscal year accounting',
            'in-force premium',
            'calendar year',
            'policy cancellation'
        ]
    },

    {
        'question_id': 'EX5-F19-Q03a',
        'domain': 'ratemaking',
        'topic': 'credibility',
        'question_text': {
            'prompt': 'Calculate the credibility-weighted indicated rate change using the classical credibility approach and trended present rates as the complement of credibility. The loss experience is considered fully credible if there is a 90% probability that the observed experience is within 2.5% of its expected value.',
            'type': 'single_part'
        },
        'inputs': [
            {
                'name': 'number_of_exposures',
                'type': 'single_value',
                'data': 20000
            },
            {
                'name': 'indicated_rate_change_before_credibility',
                'type': 'single_value',
                'data': 0.079
            },
            {
                'name': 'projected_frequency',
                'type': 'single_value',
                'data': 0.03
            },
            {
                'name': 'annual_loss_trend',
                'type': 'single_value',
                'data': -0.01
            },
            {
                'name': 'annual_premium_trend',
                'type': 'single_value',
                'data': 0.015
            },
            {
                'name': 'target_effective_date',
                'type': 'single_value',
                'data': '2019-01-01'
            },
            {
                'name': 'prior_indicated_rate_change',
                'type': 'single_value',
                'data': 0.08
            },
            {
                'name': 'prior_implemented_rate_change',
                'type': 'single_value',
                'data': 0.035
            },
            {
                'name': 'prior_effective_date',
                'type': 'single_value',
                'data': '2017-01-01'
            },
            {
                'name': 'credibility_probability',
                'type': 'single_value',
                'data': 0.90
            },
            {
                'name': 'credibility_range',
                'type': 'single_value',
                'data': 0.025
            },
            {
                'name': 'normal_distribution_table',
                'type': 'table',
                'data': [
                    {'p': 0.800, 'z': 0.842},
                    {'p': 0.850, 'z': 1.036},
                    {'p': 0.900, 'z': 1.282},
                    {'p': 0.950, 'z': 1.645},
                    {'p': 0.975, 'z': 1.960},
                    {'p': 0.990, 'z': 2.326}
                ]
            }
        ],
        'expected_answer': {
            'type': 'point_estimate',
            'value': 0.0248,
            'tolerance': 0.0001
        },
        'source': 'CAS Exam 5, Fall 2019, Question 3a',
        'tags': [
            'credibility',
            'indicated rate change',
            'classical credibility',
            'trended present rates',
            'premium trend',
            'loss trend'
        ]
    },

    {
        'question_id': 'EX5-F19-Q05ab',
        'domain': 'ratemaking',
        'topic': 'loss trend',
        'question_text': {
            'prompt': 'The following is to be used in developing a rate indication effective January 1, 2021:\n- Indication is based on accident year experience\n- Historical experience is from accident year 2018\n- Annual loss trend is +2%',
            'type': 'multi_part',
            'parts': {
                'a': 'Calculate the appropriate loss trend factor to trend from 7/1/2018 to 1/1/2022.',
                'b': 'Calculate the appropriate loss trend factor to trend from 1/1/2019 to 1/1/2022.'
            }
        },
        'expected_answer': {
            'type': 'multi_part_numeric',
            'parts': {
                'a': {
                    'value': 1.072,
                    'tolerance': 0.001
                },
                'b': {
                    'value': 1.061,
                    'tolerance': 0.001
                }
            }
        },
        'source': 'CAS Exam 5, Fall 2019, Question 5 a & b',
        'tags': [
            'loss trend',
            'trend factor calculation',
            'ratemaking'
        ]
    },

    {
        'question_id': 'EX5-F19-Q07',
        'domain': 'ratemaking',
        'topic': 'rate_indication',
        'question_text': {
            'prompt': (
                "Given the following data as of December 31, 2018, calculate the indicated rate change for policies effective January 1, 2020 "
                "using the reported Bornhuetter‐Ferguson technique for the last three accident years, "
                "given the data provided."
            ),
            'type': 'single_part'
        },
        'inputs': [
            {
                'name': 'reported_loss_alae',
                'type': 'table',
                'data': [
                    {'accident_year': 2016, 'reported_12': 3440000, 'reported_24': 4107000, 'reported_36': 4522000},
                    {'accident_year': 2017, 'reported_12': 3427000, 'reported_24': 4109000, 'reported_36': None},
                    {'accident_year': 2018, 'reported_12': 3545000, 'reported_24': None, 'reported_36': None}
                ]
            },
            {
                'name': 'calendar_year_premium_fixed_expenses',
                'type': 'table',
                'data': [
                    {'calendar_year': 2016, 'earned_premium': 10500000, 'fixed_expenses': 1155000},
                    {'calendar_year': 2017, 'earned_premium': 12000000, 'fixed_expenses': 3600000},
                    {'calendar_year': 2018, 'earned_premium': 12500000, 'fixed_expenses': 1500000}
                ]
            },
            {
                'name': 'rate_change_history',
                'type': 'table',
                'data': [
                    {'effective_date': '2017-07-01', 'change': 0.05},
                    {'effective_date': '2018-07-01', 'change': 0.02}
                ]
            },
            {'name': 'annual_loss_trend', 'type': 'single_value', 'data': 0.04},
            {'name': 'annual_premium_trend', 'type': 'single_value', 'data': 0.03},
            {'name': 'expected_loss_alae_ratio', 'type': 'single_value', 'data': 0.60},
            {'name': 'variable_expense_ratio', 'type': 'single_value', 'data': 0.30},
            {'name': 'profit_contingencies_provision', 'type': 'single_value', 'data': 0.05},
            {'name': 'ulae_provision', 'type': 'single_value', 'data': 0.07},
            {'name': 'tail_factor_36_to_ultimate', 'type': 'single_value', 'data': 1.031},
            {
                'name': 'notes',
                'type': 'notes',
                'data': (
                    "In 2017 the company implemented a new policy issuance system. "
                    "Rates are in effect for one year; all policies are annual and written evenly throughout each calendar year."
                )
            }
        ],
        'expected_answer': {
            'type': 'point_estimate',
            'value': -0.12,
            'tolerance': 0.001
        },
        'source': 'CAS Exam 5, Fall 2019, Question 7',
        'tags': [
            'ratemaking',
            'Bornhuetter-Ferguson',
            'rate_indication',
            'loss_ratio',
            'trended_present_rates'
        ]
    },

    {
        'question_id': 'EX5-F19-Q13',
        'domain': 'ratemaking',
        'topic': 'increased limit factor',
        'question_text': {
            'prompt': 'Given the following information, calculate the indicated increased limit factor for the $200,000 limit.',
            'type': 'single_part'
        },
        'inputs': [
            {
                'name': 'policy_data',
                'type': 'table',
                'data': [
                    {'policy_limit': 50000, 'claims': 145, 'pct_at_limit': 1.0},
                    {'policy_limit': 100000, 'claims': 550, 'pct_at_limit': 0.6},
                    {'policy_limit': 200000, 'claims': 875, 'pct_at_limit': 0.4}
                ]
            },
            {
                'name': 'notes',
                'type': 'notes',
                'data': (
                    'All claim payments are either 50% of the policy limit or 100% of the policy limit.\n'
                    '$50,000 is the basic limit.'
                )
            }
        ],
        'expected_answer': {
            'type': 'point_estimate',
            'value': 2.646,
            'tolerance': 0.001
        },
        'source': 'CAS Exam 5, Fall 2019, Question 13',
        'tags': ['ILF', 'limited average severity', 'ratemaking']
    },

    {
        'question_id': 'EX5-F19-Q18a',
        'domain': 'reserving',
        'topic': 'case outstanding development',
        'question_text': {
            'prompt': 'Estimate unpaid claims for accident year 2018 as of December 31, 2018 using a case outstanding development technique.',
            'type': 'single_part'
        },
        'inputs': [
            {
                'name': 'cumulative_paid_claims',
                'type': 'table',
                'data': [
                    {'accident_year': 2015, 'paid_12': 1200000, 'paid_24': 2325000, 'paid_36': 2900000, 'paid_48': 3100000},
                    {'accident_year': 2016, 'paid_12': 1800000, 'paid_24': 3300000, 'paid_36': 4100000, 'paid_48': None},
                    {'accident_year': 2017, 'paid_12': 1500000, 'paid_24': 2800000, 'paid_36': None, 'paid_48': None},
                    {'accident_year': 2018, 'paid_12': 1700000, 'paid_24': None, 'paid_36': None, 'paid_48': None}
                ]
            },
            {
                'name': 'case_outstanding',
                'type': 'table',
                'data': [
                    {'accident_year': 2015, 'os_12': 1500000, 'os_24': 800000,  'os_36': 400000,  'os_48': 160000},
                    {'accident_year': 2016, 'os_12': 2000000, 'os_24': 1150000, 'os_36': 575000,  'os_48': None},
                    {'accident_year': 2017, 'os_12': 1750000, 'os_24': 975000,  'os_36': None, 'os_48': None},
                    {'accident_year': 2018, 'os_12': 2200000, 'os_24': None, 'os_36': None, 'os_48': None}
                ]
            },
            {
                'name': 'development_factor_48_to_ult',
                'type': 'single_value',
                'data': 1.15
            },
            {
                'name': 'notes',
                'type': 'notes',
                'data': 'There is no paid or reported development beyond 60 months.'
            }
        ],
        'expected_answer': {
            'type': 'point_estimate',
            'value': 3092.76,
            'tolerance': 1
        },
        'source': 'CAS Exam 5, Fall 2019, Question 18a',
        'tags': ['reserving', 'development', 'case outstanding']
    },

    {
        'question_id': 'EX5-F19-Q19',
        'domain': 'reserving',
        'topic': 'cape cod',
        'question_text': {
            'prompt': 'Given the following data as of December 31, 2018, calculate ultimate claims for accident year 2017 using the Cape Cod technique.',
            'type': 'single_part'
        },
        'inputs': [
            {
                'name': 'reported_claims_and_premium',
                'type': 'table',
                'data': [
                    {'accident_year': 2016, 'reported_claims': 7200000, 'earned_premium': 10400000},
                    {'accident_year': 2017, 'reported_claims': 6300000, 'earned_premium': 11000000},
                    {'accident_year': 2018, 'reported_claims': 4700000, 'earned_premium': 11500000}
                ]
            },
            {
                'name': 'age_to_ultimate_factors',
                'type': 'table',
                'data': [
                    {'age_to_ult': '12-ult', 'factor': 1.764},
                    {'age_to_ult': '24-ult', 'factor': 1.260},
                    {'age_to_ult': '36-ult', 'factor': 1.050},
                    {'age_to_ult': '48-ult', 'factor': 1.000}
                ]
            },
            {
                'name': 'annual_trends',
                'type': 'table',
                'data': [
                    {'type': 'claims', 'trend': 0.03},
                    {'type': 'premium', 'trend': 0.02}
                ]
            },
            {
                'name': 'rate_changes',
                'type': 'table',
                'data': [
                    {'effective_date': '2016-07-01', 'rate_change': 0.04},
                    {'effective_date': '2017-07-01', 'rate_change': 0.02}
                ]
            },
            {
                'name': 'notes',
                'type': 'notes',
                'data': 'All policies have an annual term and are written evenly throughout the year.'
            }
        ],
        'expected_answer': {
            'type': 'point_estimate',
            'value': 7932000,
            'tolerance': 600
        },
        'source': 'CAS Exam 5, Fall 2019, Question 19',
        'tags': ['cape cod', 'reserving', 'development']
    },

    {
        'question_id': 'EX5-F19-Q20a',
        'domain': 'reserving',
        'topic': 'frequency-severity disposal rate',
        'question_text': {
            'prompt': 'Use the frequency-severity disposal rate technique to estimate unpaid claims for accident year 2018.',
            'type': 'single_part'
        },
        'inputs': [
            {
                'name': 'closed_claim_counts',
                'type': 'table',
                'data': [
                    {'accident_year': 2015, 'closed_12': 308, 'closed_24': 555, 'closed_36': 642, 'closed_48': 647, 'ultimate_count': 647},
                    {'accident_year': 2016, 'closed_12': 356, 'closed_24': 563, 'closed_36': 678, 'closed_48': None, 'ultimate_count': 683},
                    {'accident_year': 2017, 'closed_12': 358, 'closed_24': 575, 'closed_36': None, 'closed_48': None, 'ultimate_count': 684},
                    {'accident_year': 2018, 'closed_12': 402, 'closed_24': None, 'closed_36': None, 'closed_48': None, 'ultimate_count': 795}
                ]
            },
            {
                'name': 'cumulative_paid_claims',
                'type': 'table',
                'data': [
                    {'accident_year': 2015, 'paid_12': 375000, 'paid_24': 745000, 'paid_36': 906000, 'paid_48': 916000},
                    {'accident_year': 2016, 'paid_12': 397000, 'paid_24': 750000, 'paid_36': 922000, 'paid_48': None},
                    {'accident_year': 2017, 'paid_12': 422000, 'paid_24': 762000, 'paid_36': None,    'paid_48': None},
                    {'accident_year': 2018, 'paid_12': 385000, 'paid_24': None,    'paid_36': None,    'paid_48': None}
                ]
            },
            {
                'name': 'notes',
                'type': 'notes',
                'data': (
                    'A court decision on December 31, 2018 will increase future claim payments by 20%.\n'
                    'All claims are closed by age 48.\n'
                    'There is no severity trend.'
                )
            }
        ],
        'expected_answer': {
            'type': 'point_estimate',
            'value': 764848,
            'tolerance': 1
        },
        'source': 'CAS Exam 5, Fall 2019, Question 20a',
        'tags': ['frequency-severity disposal rate', 'reserving', 'disposal rate']
    },

    {
        'question_id': 'EX5-F19-Q21',
        'domain': 'reserving',
        'topic': 'berquist-sherman',
        'question_text': {
            'prompt': 'Calculate unpaid claims for accident year 2018 using the reported Berquist-Sherman technique.',
            'type': 'single_part'
        },
        'inputs': [
            {
                'name': 'reported_claims',
                'type': 'table',
                'data': [
                    {'accident_year': 2015, 'reported_12': 1100000, 'reported_24': 1650000, 'reported_36': 1675000, 'reported_48': 1680000},
                    {'accident_year': 2016, 'reported_12': 1250000, 'reported_24': 1680000, 'reported_36': 1750000, 'reported_48': None},
                    {'accident_year': 2017, 'reported_12': 1200000, 'reported_24': 1800000, 'reported_36': None,    'reported_48': None},
                    {'accident_year': 2018, 'reported_12': 1500000, 'reported_24': None,    'reported_36': None,    'reported_48': None}
                ]
            },
            {
                'name': 'reported_claim_counts',
                'type': 'table',
                'data': [
                    {'accident_year': 2015, 'count_12': 108, 'count_24': 115, 'count_36': 115, 'count_48': 115},
                    {'accident_year': 2016, 'count_12': 112, 'count_24': 120, 'count_36': 120, 'count_48': None},
                    {'accident_year': 2017, 'count_12': 104, 'count_24': 110, 'count_36': None,  'count_48': None},
                    {'accident_year': 2018, 'count_12': 106, 'count_24': None,  'count_36': None,  'count_48': None}
                ]
            },
            {
                'name': 'paid_claims',
                'type': 'table',
                'data': [
                    {'accident_year': 2015, 'paid_12': 560000, 'paid_24': 1325000, 'paid_36': 1650000, 'paid_48': 1680000},
                    {'accident_year': 2016, 'paid_12': 650000, 'paid_24': 1350000, 'paid_36': 1720000, 'paid_48': None},
                    {'accident_year': 2017, 'paid_12': 615000, 'paid_24': 1305000, 'paid_36': None,    'paid_48': None},
                    {'accident_year': 2018, 'paid_12': 625000, 'paid_24': None,    'paid_36': None,    'paid_48': None}
                ]
            },
            {
                'name': 'closed_claim_counts',
                'type': 'table',
                'data': [
                    {'accident_year': 2015, 'closed_12': 78, 'closed_24': 106, 'closed_36': 114, 'closed_48': 115},
                    {'accident_year': 2016, 'closed_12': 80, 'closed_24': 111, 'closed_36': 118, 'closed_48': None},
                    {'accident_year': 2017, 'closed_12': 75, 'closed_24':  99, 'closed_36': None, 'closed_48': None},
                    {'accident_year': 2018, 'closed_12': 82, 'closed_24': None, 'closed_36': None, 'closed_48': None}
                ]
            },
            {
                'name': 'severity_trend',
                'type': 'single_value',
                'data': 0.05
            },
            {
                'name': 'notes',
                'type': 'notes',
                'data': 'Exposures have remained constant throughout all accident years.'
            }
        ],
        'expected_answer': {
            'type': 'point_estimate',
            'value': 1006000,
            'tolerance': 3000
        },
        'source': 'CAS Exam 5, Fall 2019, Question 21',
        'tags': ['berquist-sherman', 'reported development', 'reserving']
    },

    {
        'question_id': 'EX5-F19-Q24a',
        'domain': 'reserving',
        'topic': 'ULAE',
        'question_text': {
            'prompt': 'Calculate unpaid ULAE at December 31, 2018 using the Kittel refinement.',
            'type': 'single_part'
        },
        'inputs': [
            {
                'name': 'calendar_year_data',
                'type': 'table',
                'data': [
                    {'calendar_year': 2015, 'paid_claims': 18700, 'incurred_claims': 35500, 'paid_ulae': 1870},
                    {'calendar_year': 2016, 'paid_claims': 19200, 'incurred_claims': 36500, 'paid_ulae': 1890},
                    {'calendar_year': 2017, 'paid_claims': 18900, 'incurred_claims': 36400, 'paid_ulae': 1910},
                    {'calendar_year': 2018, 'paid_claims': 19800, 'incurred_claims': 37400, 'paid_ulae': 1990}
                ]
            },
            {
                'name': 'report_year_data',
                'type': 'table',
                'data': [
                    {'report_year': 2015, 'earned_premium': 77600, 'paid_claims': 22400, 'reported_claims': 29500, 'pct_unreported': 0.107},
                    {'report_year': 2016, 'earned_premium': 78000, 'paid_claims': 14300, 'reported_claims': 26200, 'pct_unreported': 0.231},
                    {'report_year': 2017, 'earned_premium': 77800, 'paid_claims': 5500,  'reported_claims': 20700, 'pct_unreported': 0.559},
                    {'report_year': 2018, 'earned_premium': 77900, 'paid_claims': 2800,  'reported_claims': 19000, 'pct_unreported': 0.763}
                ]
            },
            {
                'name': 'expected_claims_ratio',
                'type': 'single_value',
                'data': 0.45
            },
            {
                'name': 'notes',
                'type': 'notes',
                'data': 'All policies are claims-made.'
            }
        ],
        'expected_answer': {
            'type': 'point_estimate',
            'value': 3800,
            'tolerance': 60
        },
        'source': 'CAS Exam 5, Fall 2019, Question 24a',
        'tags': ['ulae', 'kittel refinement', 'reserving']
    },

    {
    'question_id': 'EX5-F19-Q25a',
    'domain': 'reserving',
    'topic': 'paid development',
    'question_text': {
        'prompt': 'Calculate the accident year 2018 expected net paid claims for the period 15 to 18 months based on the method specified.',
        'type': 'multi_part',
        'parts': {
            'i': 'Assuming claims emerge uniformly between evaluation points.',
            'ii': 'Using the industry payment pattern.'
        }
    },
    'inputs': [
        {
            'name': 'development_factors',
            'type': 'table',
            'data': [
                {'description': '12-ultimate gross paid claims development factor', 'value': 5.00},
                {'description': '24-ultimate gross paid claims development factor', 'value': 3.30}
            ]
        },
        {
            'name': 'paid_gross_12m',
            'type': 'single_value',
            'data': 12000000
        },
        {
            'name': 'industry_payment_pattern_12_24',
            'type': 'table',
            'data': [
                {'interval': '12-15 months', 'percent_paid': 0.50},
                {'interval': '15-18 months', 'percent_paid': 0.35},
                {'interval': '18-21 months', 'percent_paid': 0.10},
                {'interval': '21-24 months', 'percent_paid': 0.05}
            ]
        },
        {
            'name': 'actual_net_paid_15_18',
            'type': 'single_value',
            'data': 1450000
        },
        {
            'name': 'quota_share_ceded',
            'type': 'single_value',
            'data': 0.30
        },
        {
            'name': 'notes',
            'type': 'notes',
            'data': 'Ultimate losses are estimated using the paid development technique.'
        }
    ],
    'expected_answer': {
        'type': 'multi_part',
        'parts': {
            'i': {'value': 1081818, 'tolerance': 1},
            'ii': {'value': 1514545, 'tolerance': 1}
        }
    },
    'source': 'CAS Exam 5, Fall 2019, Question 25a',
    'tags': ['paid development', 'reserving', 'quota share']
}

] 