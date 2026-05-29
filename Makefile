# Cyber-Range Lab — Top-Level Makefile
# Vollstaendige Lab-Lifecycle-Automatisierung

.PHONY: help lab-up lab-down lab-status lab-snapshot lab-restore preauth keys-rotate test lint clean

help:
	@echo "Cyber-Range Lab — verfuegbare Targets:"
	@echo ""
	@echo "  lab-up         Lab hochfahren (terraform apply + ansible run, ~10 min)"
	@echo "  lab-down       Lab abbauen + finalen Snapshot in Object Storage"
	@echo "  lab-status     Health-Check aller Komponenten"
	@echo "  lab-snapshot   Manueller Phase-Snapshot fuer Replay"
	@echo "  lab-restore    Restore von letztem Snapshot"
	@echo "  preauth        Neue Pre-Auth-Keys fuer alle Workstations generieren"
	@echo "  keys-rotate    SSH-Keys + Vault-Master-PW rotieren"
	@echo "  test           pytest auf Hermes-GM-Skill + Ansible-Syntax-Check"
	@echo "  lint           Terraform-fmt + ansible-lint + yamllint"
	@echo "  clean          Lokale Artefakte loeschen (kein Hetzner-Teardown!)"

lab-up:
	@bash scripts/lab-up.sh

lab-down:
	@bash scripts/lab-down.sh

lab-status:
	@bash scripts/lab-status.sh

lab-snapshot:
	@bash scripts/lab-snapshot.sh

lab-restore:
	@bash scripts/lab-restore.sh

preauth:
	@bash scripts/gen-preauth-keys.sh

keys-rotate:
	@bash scripts/keys-rotate.sh

test:
	@cd hermes-gm-skill && python -m pytest -v
	@cd ansible && ansible-playbook --syntax-check playbooks/*.yml

lint:
	@cd terraform && terraform fmt -check -recursive
	@ansible-lint ansible/
	@yamllint ansible/ docs/ briefings/

clean:
	@rm -rf terraform/.terraform terraform/*.tfstate.backup
	@rm -rf ansible/inventory.ini ansible/inventory.yml
	@find . -name "*.retry" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Lokale Artefakte geloescht. Hetzner-VMs bleiben — fuer Teardown: make lab-down"
