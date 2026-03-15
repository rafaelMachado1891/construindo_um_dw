#!/usr/bin/env bash

# Use this file with: source activate_git_bash.sh
# It forces Git Bash to use the project's virtualenv executables.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Use: source activate_git_bash.sh"
  exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
VENV_PYTHON="${VENV_DIR}/Scripts/python.exe"

if [[ ! -f "${VENV_PYTHON}" ]]; then
  echo "Virtualenv nao encontrada em ${VENV_DIR}"
  return 1
fi

source "${VENV_DIR}/Scripts/activate"

alias python="${VENV_PYTHON}"
alias python3="${VENV_PYTHON}"
pip() {
  "${VENV_PYTHON}" -m pip "$@"
}

deactivate_project_venv() {
  unalias python 2>/dev/null
  unalias python3 2>/dev/null
  unset -f pip 2>/dev/null
  if declare -F deactivate >/dev/null; then
    deactivate
  fi
  unset -f deactivate_project_venv 2>/dev/null
}

hash -r 2>/dev/null

echo "Virtualenv ativa em ${VENV_DIR}"
echo "Python em uso: $("${VENV_PYTHON}" -c 'import sys; print(sys.executable)')"
