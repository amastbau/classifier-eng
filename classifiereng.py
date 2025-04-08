class LogClassifier:
    def __init__(self):
        self.classifiers = {
            "before-backup": self.is_before_backup,
            "backup-missing": self.is_backup_missing,
            "oadp-backup": self.is_oadp_backup_failure,
            "oadp-restore": self.is_oadp_restore_failure,
            "backup_or_restore_validation": self.is_validation_failure,
            "restore-failure": self.is_restore_failure,
            "vsl-missing": self.is_vsl_missing,
            "backup-partially-failed": self.is_backup_partially_failed,
            "internal-registry-error": self.is_internal_registry_error,
            "backup-partiallyfailed": self.is_backup_partiallyfailed,
            "backup-inprogress": self.is_backup_inprogress,
            "app_validation": self.is_app_validation,
            "app_deploy": self.is_app_deploy,
            "backup_expected_completed_and_failed": self.is_backup_expected_completed_and_failed,
            "dataupload_accepted": self.is_dataupload_accepted,
            "restore_phase_finalizing_partially_failed": self.is_restore_phase_finalizing_partially_failed,
            "app_failure": self.is_app_failure,
            "namespace_deletion_failure": self.is_namespace_deletion_failure,
            "error_patch_for_managed_fields": self.is_error_patch_for_managed_fields,
            "empty_file_after_restore": self.is_empty_file_after_restore,
            "restore_is_not_partiallyfailed": self.is_restore_is_not_partiallyfailed,
            "restore_partiallyfailed": self.is_restore_partiallyfailed,
            "operatorcondition_patch": self.is_operatorcondition_patch_failure,
        }

    def classify(self, content: str) -> List[str]:
        matches = []
        for name, method in self.classifiers.items():
            result = method(content)
            if result:
                if isinstance(result, list):
                    matches.extend(result)
                else:
                    matches.append(name)
        return list(set(matches))

    def is_error_patch_for_managed_fields(self, content: str) -> bool:
        return re.search(r"error patch for managed fields \w+\/\w+-[\w\d]+: secrets", content, re.IGNORECASE) is not None

    def is_before_backup(self, content: str) -> bool:
        return re.search(r"no indication of any backup in the log", content, re.IGNORECASE) is not None

    def is_backup_missing(self, content: str) -> bool:
        return re.search(r"Backup.velero.io \"backup\" not found", content, re.IGNORECASE) is not None

    def is_oadp_backup_failure(self, content: str) -> bool:
        return re.search(r"backup failed|failure during backup", content, re.IGNORECASE) is not None

    def is_oadp_restore_failure(self, content: str) -> bool:
        return re.search(r"restore phase is: Failed", content, re.IGNORECASE) is not None

    def is_validation_failure(self, content: str) -> bool:
        return re.search(r"validation errors", content, re.IGNORECASE) is not None

    def is_restore_failure(self, content: str) -> bool:
        return re.search(r"restore phase is: Failed", content, re.IGNORECASE) is not None

    def is_vsl_missing(self, content: str) -> bool:
        return re.search(r"VSL missing", content, re.IGNORECASE) is not None

    def is_backup_partially_failed(self, content: str) -> bool:
        return re.search(r"backup partially failed", content, re.IGNORECASE) is not None

    def is_internal_registry_error(self, content: str) -> bool:
        return re.search(r"internal registry error", content, re.IGNORECASE) is not None

    def is_backup_partiallyfailed(self, content: str) -> bool:
        return re.search(r"backup partiallyfailed", content, re.IGNORECASE) is not None

    def is_backup_inprogress(self, content: str) -> bool:
        return re.search(r"restore phase is: InProgress", content, re.IGNORECASE) is not None

    def is_app_validation(self, content: str) -> bool:
        return re.search(r"with_validation", content, re.IGNORECASE) is not None

    def is_app_deploy(self, content: str) -> bool:
        return re.search(r"with_deploy", content, re.IGNORECASE) is not None

    def is_backup_expected_completed_and_failed(self, content: str) -> bool:
        return re.search(r"Expected.*<v1\.BackupPhase>: Completed.*Failed|FinalizingPartiallyFailed|PartiallyFailed", content, re.IGNORECASE) is not None

    def is_dataupload_accepted(self, content: str) -> bool:
        return re.search(r"Timed out after \d+\.\d+s.*DataUpload.*phase is: Accepted; expected: Completed", content, re.IGNORECASE | re.DOTALL) is not None

    def is_restore_phase_finalizing_partially_failed(self, content: str) -> bool:
        return re.search(r"restore phase is: FinalizingPartiallyFailed; expected: Completed", content, re.IGNORECASE) is not None

    def is_empty_file_after_restore(self, content: str) -> bool:
        return re.search(r"Expected file .+ to be non-empty, but its size is 0", content, re.IGNORECASE) is not None

    def is_restore_is_not_partiallyfailed(self, content: str) -> bool:
        return re.search(r"Restore is expected to party fail!.*Expected\s*<bool>: false\s*to be true", content, re.IGNORECASE) is not None

    def is_restore_partiallyfailed(self, content: str) -> bool:
        return re.search(r"backup phase is: PartiallyFailed; expected: Completed", content, re.IGNORECASE) is not None

    def is_namespace_deletion_failure(self, content: str) -> bool:
        return re.search(r'Failed!.*"Namespace" ".*": Timed out waiting on resource', content, re.IGNORECASE) is not None

    def is_app_failure(self, content: str) -> List[str]:
        matches = []
        roles = re.findall(r'"use_role":"([^"]+)"', content)
        for role in roles:
            role_name = role.split('/')[-1]
            if re.search(r'"with_cleanup":true', content):
                matches.append(f'app_{role_name}_cleanup')
            if re.search(r'"with_deploy":true', content):
                matches.append(f'app_{role_name}_deploy')
            if re.search(r'"with_validate":true', content):
                matches.append(f'app_{role_name}_validate')
        return matches

    def is_operatorcondition_patch_failure(self, content: str) -> bool:
        pattern = (
            r"(?s)^Run the command:\n"
            r"oc get OperatorCondition -n openshift-adp -o jsonpath='\{\.items\[\]\.metadata\.name\}' \| awk -F 'v' '\{print \$2\}'\n"
            r"Run the command:\n"
            r"oc get OperatorCondition -n openshift-adp -o jsonpath='\{\.items\[\]\.metadata\.name\}' \| awk -F 'v' '\{print \$2\}'\n\n+"
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\n"
            r"\[FAILED\] Failed after \d+(?:\.\d+)?s\.\n"
            r"Expected\n"
            r"\s*:\s*true\n"
            r"to be false$"
        )
        return re.search(pattern, content) is not None