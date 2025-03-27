FROM rust:1.76-slim as builder

WORKDIR /app

# Instalar dependências
RUN apt-get update && \
    apt-get install -y pkg-config libssl-dev curl && \
    rustup target add wasm32-wasip1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar arquivos do projeto
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# Compilar o projeto
RUN cargo build --target wasm32-wasip1 --release

# Estágio Node.js
FROM node:20-slim

WORKDIR /app

# Instalar dependências
COPY package.json package-lock.json ./
RUN npm ci

# Copiar servidor e WASM compilado
COPY server.js .env.example ./
COPY --from=builder /app/target/wasm32-wasip1/release/mcp_server_tess_xtp.wasm ./target/wasm32-wasip1/release/

# Configurar variáveis de ambiente
ENV NODE_ENV=production
ENV PORT=3000

# Expor porta
EXPOSE 3000

# Iniciar servidor
CMD ["node", "server.js"] 