# LEAPP Testing Documentation

This documentation provides an overview of the testing processes and components used in the LEAPP project. It covers module testing, test data creation, and image management.

## Table of Contents

1. [Testing Architecture Overview](testing_architecture_overview.md)
   - Overview of the LEAPP testing components and workflow
   - Description of key features and future considerations

2. [Creating Module Test Cases](create_module_test_cases.md)
   - Detailed guide on using the `make_test_data.py` script
   - Process of generating test data for LEAPP modules

3. [Testing Modules](testing_modules.md)
   - Instructions for running tests on LEAPP modules using the `test_module.py` script
   - Explanation of test execution, result collection, and golden file testing

4. [Documenting Conditional Logic & Coverage](conditional_logic_coverage.md)
   - How to use `admin/test/metadata/conditional_behaviors.json`
   - Documenting module-specific conditions (e.g., iOS versions)
   - Linking conditions to test cases for coverage analysis

5. [Testing Module Outputs](testing_module_outputs.md)
   - Guide for verifying various output formats supported by modules using the `test_module_output.py` script
   - Process of manual output verification

6. [Adding New Images to the Manifest](guide_adding_images.md)
   - Step-by-step guide for adding new test images to the project
   - Best practices for maintaining the [image manifest](../../image_manifest.json)

7. [File Path Analysis](filepath_analysis.md)
   - Overview of the file path search process
   - Explanation of [filepath_results.csv](../filepath_results.csv) and [filepath_search_summary.md](../filepath_search_summary.md)

## Getting Started

To begin working with LEAPP testing:

1. Review the [Testing Architecture Overview](testing_architecture_overview.md) to understand the overall structure.
2. Follow the [Creating Module Test Cases](create_module_test_cases.md) guide to generate test data for modules using the `make_test_data.py` script.
3. Use the [Testing Modules](testing_modules.md) document to run tests with the `test_module.py` script and understand the golden file workflow.
4. Refer to [Documenting Conditional Logic & Coverage](conditional_logic_coverage.md) to understand how to document and track tests for specific module behaviors.
5. Use [Testing Module Outputs](testing_module_outputs.md) to verify report outputs with the `test_module_output.py` script.
6. If you need to add a new test image, refer to [Adding New Images to the Manifest](guide_adding_images.md).


