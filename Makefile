TOOL_NAME := what-to-do

.PHONY: install-cli-local
install-cli-local:
	uv tool install --force .
	@printf "✅ Installed $(TOOL_NAME)\n"
	$(TOOL_NAME) config set client_mode local
	@printf "✅ Set up local client\n"
	$(TOOL_NAME) --install-completion
	@printf "✅ Installed shell completions\n"
	@printf "\n✅ Installation successful\n"

.PHONY: uninstall-cli
uninstall-cli:
	uv tool uninstall $(TOOL_NAME)
	@printf "✅ Uninstalled $(TOOL_NAME)\n"
	@printf "\n✅ Uninstallation successful\n"