FROM ollama/ollama:latest

# Install necessary tools using apt (Debian/Ubuntu)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    dos2unix \
    curl && \
    rm -rf /var/lib/apt/lists/*

# --- DEBUG STEP 1 ---
# Show initial working directory contents
RUN echo "DEBUG 1: Initial working directory contents:" && \
    pwd && ls -la

# Copy the entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh

# --- DEBUG STEP 2 ---
# Verify file copy and permissions
RUN echo "DEBUG 2: Root directory after COPY:" && ls -la / && \
    echo "DEBUG 3: Entrypoint script permissions:" && ls -la /entrypoint.sh && \
    echo "DEBUG 4: Entrypoint script first lines:" && head -5 /entrypoint.sh

# Fix line endings and set secure permissions
RUN dos2unix /entrypoint.sh && \
    chmod 750 /entrypoint.sh && \
    chown root:root /entrypoint.sh

# Verify final permissions and validate script
RUN echo "DEBUG 5: Final entrypoint permissions:" && \
    ls -la /entrypoint.sh && \
    echo "DEBUG 6: Script validation:" && \
    bash -n /entrypoint.sh && \
    echo "Script syntax is valid"

# Health check to verify service availability
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s \
    CMD curl -f http://localhost:11434 || exit 1

COPY scripts/fix-permissions.sh /fix-permissions.sh
RUN chmod +x /fix-permissions.sh

ENTRYPOINT ["/fix-permissions.sh && /entrypoint.sh"]