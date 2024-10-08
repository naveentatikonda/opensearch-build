# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.


import os
import unittest
from unittest.mock import MagicMock, call, patch

from manifests.test_manifest import TestManifest
from report_workflow.test_report_runner import TestReportRunner
from system.temporary_directory import TemporaryDirectory


class TestTestReportRunnerDashboards(unittest.TestCase):
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH = os.path.join(DATA_DIR, "test-manifest-opensearch-dashboards.yml")
    TEST_MANIFEST_OPENSEARCH_DASHBOARDS = TestManifest.from_path(TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH)

    @patch("report_workflow.report_args.ReportArgs")
    def test_runner_dashboards_init(self, report_args_mock: MagicMock) -> None:
        report_args_mock.test_manifest_path = self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH
        report_args_mock.artifact_paths = {"opensearch-dashboards": self.DATA_DIR}
        report_args_mock.test_run_id = 123
        report_args_mock.base_path = self.DATA_DIR
        report_args_mock.test_type = "integ-test"
        report_args_mock.release_candidate = "100"

        test_report_runner = TestReportRunner(report_args_mock, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS)
        test_report_runner_data = test_report_runner.update_data()
        self.assertEqual(test_report_runner.name, "opensearch-dashboards")
        self.assertEqual(test_report_runner.test_run_id, 123)
        self.assertEqual(test_report_runner.test_type, "integ-test")
        self.assertEqual(test_report_runner.test_manifest_path, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH)
        self.assertEqual(test_report_runner_data["version"], "1.3.18")
        self.assertEqual(test_report_runner_data["platform"], "linux")
        self.assertEqual(test_report_runner_data["architecture"], "x64")
        self.assertEqual(test_report_runner_data["distribution"], "tar")
        self.assertEqual(test_report_runner_data["id"], "7791")
        self.assertEqual(test_report_runner_data["rc"], "100")

    @patch("report_workflow.report_args.ReportArgs")
    def test_generate_file(self, report_args_mock: MagicMock) -> None:
        report_args_mock.test_manifest_path = self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH
        report_args_mock.artifact_paths = {"opensearch-dashboards": self.DATA_DIR}
        report_args_mock.test_run_id = 123
        report_args_mock.base_path = self.DATA_DIR
        report_args_mock.test_type = "integ-test"
        report_args_mock.release_candidate = "100"

        test_report_runner = TestReportRunner(report_args_mock, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS)
        test_report_runner_data = test_report_runner.update_data()

        with TemporaryDirectory() as path:
            output_path = os.path.join(path.name, "test-report.yml")
            test_report_runner.generate_report(test_report_runner_data, path.name)
            self.assertTrue(os.path.isfile(output_path))

    @patch("report_workflow.report_args.ReportArgs")
    def test_ci_group(self, report_args_mock: MagicMock) -> None:
        report_args_mock.test_manifest_path = self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH
        report_args_mock.artifact_paths = {"opensearch-dashboards": self.DATA_DIR}
        report_args_mock.test_run_id = 123
        report_args_mock.base_path = self.DATA_DIR
        report_args_mock.test_type = "integ-test"
        report_args_mock.release_candidate = "100"

        test_report_runner = TestReportRunner(report_args_mock, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS)
        test_report_runner_data = test_report_runner.update_data()

        self.assertEqual(len(test_report_runner_data["components"]), 9)
        for i in range(3):
            self.assertEqual(test_report_runner_data["components"][i]["name"], f"OpenSearch-Dashboards-ci-group-{i + 1}")

        for i in range(len(self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS.components.__to_dict__())):
            if self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS.components.__to_dict__()[i]["name"] == "OpenSearch-Dashboards":
                continue
            else:
                self.assertEqual(self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS.components.__to_dict__()[i]["name"],
                                 test_report_runner_data["components"][i + 2]["name"])

    @patch("yaml.safe_load")
    @patch("urllib.request.urlopen")
    @patch("validators.url")
    @patch("report_workflow.report_args.ReportArgs")
    def test_runner_component_entry_url(self, report_args_mock: MagicMock, validators_mock: MagicMock,
                                        urlopen_mock: MagicMock, yaml_safe_load_mock: MagicMock) -> None:
        report_args_mock.test_manifest_path = self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH
        report_args_mock.artifact_paths = {"opensearch-dashboards": "foo/bar"}
        report_args_mock.test_run_id = 123
        report_args_mock.base_path = "https://ci.opensearch.org/ci/dbc/mock"
        report_args_mock.test_type = "integ-test"

        validators_mock.return_value = True
        yaml_safe_load_mock.return_value = {"test_result": "PASS"}
        urlopen_mock.return_value = MagicMock()

        test_report_component_dict = TestReportRunner(report_args_mock, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS).component_entry("alertingDashboards")
        urlopen_mock.assert_has_calls([call(
            'https://ci.opensearch.org/ci/dbc/mock/test-results/123/integ-test/alertingDashboards/with-security/alertingDashboards.yml')])
        self.assertEqual(test_report_component_dict.get("configs")[0]["status"], "PASS")
        self.assertEqual(test_report_component_dict.get("configs")[0]["name"], "with-security")
        self.assertEqual(test_report_component_dict.get("configs")[0]["yml"],
                         "https://ci.opensearch.org/ci/dbc/mock/test-results/123/integ-test/alertingDashboards/with-security/alertingDashboards.yml")
        self.assertEqual(test_report_component_dict.get("configs")[0]["cluster_stdout"][0],
                         "https://ci.opensearch.org/ci""/dbc/mock/test-results/123/integ-test/alertingDashboards/with-security/local-cluster-logs/id-0/stdout.txt")
        self.assertEqual(test_report_component_dict.get("configs")[0]["cluster_stdout"][1],
                         "https://ci.opensearch.org/ci""/dbc/mock/test-results/123/integ-test/alertingDashboards/with-security/local-cluster-logs/id-1/stdout.txt")
        self.assertEqual(test_report_component_dict.get("configs")[0]["cluster_stderr"][0],
                         "https://ci.opensearch.org/ci""/dbc/mock/test-results/123/integ-test/alertingDashboards/with-security/local-cluster-logs/id-0/stderr.txt")
        self.assertEqual(test_report_component_dict.get("configs")[0]["cluster_stderr"][1],
                         "https://ci.opensearch.org/ci""/dbc/mock/test-results/123/integ-test/alertingDashboards/with-security/local-cluster-logs/id-1/stderr.txt")

        self.assertEqual(test_report_component_dict.get("configs")[1]["name"], "without-security")
        self.assertEqual(test_report_component_dict.get("configs")[1]["cluster_stdout"][0],
                         "https://ci.opensearch.org/ci""/dbc/mock/test-results/123/integ-test/alertingDashboards/without-security/local-cluster-logs/id-2/stdout.txt")
        self.assertEqual(test_report_component_dict.get("configs")[1]["cluster_stdout"][1],
                         "https://ci.opensearch.org/ci""/dbc/mock/test-results/123/integ-test/alertingDashboards/without-security/local-cluster-logs/id-3/stdout.txt")
        self.assertEqual(test_report_component_dict.get("configs")[1]["cluster_stderr"][0],
                         "https://ci.opensearch.org/ci""/dbc/mock/test-results/123/integ-test/alertingDashboards/without-security/local-cluster-logs/id-2/stderr.txt")
        self.assertEqual(test_report_component_dict.get("configs")[1]["cluster_stderr"][1],
                         "https://ci.opensearch.org/ci""/dbc/mock/test-results/123/integ-test/alertingDashboards/without-security/local-cluster-logs/id-3/stderr.txt")
