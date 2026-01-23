.PHONY: typer

help: ##:: Show this help
	@YELLOW=$$(printf '\033[1;33m'); BLUE=$$(printf '\033[0;34m'); GREEN=$$(printf '\033[0;32m'); RESET=$$(printf '\033[0m'); \
	echo ""; \
	sed -ne '/@sed/!{/^## *[╔║╚═]/s/^## *//p; s/:.*##*/ /p;}' $(MAKEFILE_LIST) \
	| awk -v yellow="$$YELLOW" -v blue="$$BLUE" -v green="$$GREEN" -v reset="$$RESET" '{ \
		match($$0,/^[^:]+/); \
		cmd=substr($$0,RSTART,RLENGTH); \
		rest=substr($$0,RLENGTH+1); \
		split(rest, parts, "::"); \
		if (length(parts) > 1) { \
			desc=parts[2]; \
			gsub(/^ */, "", desc); \
			printf "%s%s%s%s::%s %s%s\n", yellow, cmd, reset, blue, reset, green, desc, reset; \
		} else { \
			printf "%s%s%s%s\n", yellow, cmd, reset, rest; \
		} \
	}'; \
	echo ""; \
	printf "$${RESET}"

ping: ##:: Ping
	uv run cli.py ping

up: ##:: Run agent
	uv run cli.py run
