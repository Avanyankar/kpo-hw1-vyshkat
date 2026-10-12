# Рецепты на POSIX sh; на Windows sh из Git.
ifeq ($(OS),Windows_NT)
  GIT_ROOT := $(subst /mingw64/libexec/git-core,,$(subst \,/,$(shell git --exec-path)))
  ifeq ($(GIT_ROOT),)
    $(error Git for Windows не найден: рецепты выполняются его sh)
  endif
  export PATH := $(GIT_ROOT)/usr/bin;$(PATH)
  SHELL := sh.exe
  # sh не переписывает /пути.
  export MSYS_NO_PATHCONV := 1
endif

.DEFAULT_GOAL := help

.PHONY: help install run

help: ## Показать список команд
	@awk 'BEGIN {FS = ":.*## "} /^##@ / {printf "\n\033[1m%s\033[0m\n", substr($$0, 5)} /^[a-zA-Z_-]+:.*## / {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

##@ Установка

install: ## Создать .venv и установить зависимости
	uv sync --frozen

##@ Запуск

run: ## Запустить приложение
	uv run vyshkat
