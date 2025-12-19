FROM mono:6.12 AS build

WORKDIR /kilde

RUN sed -i s/deb.debian.org/archive.debian.org/g /etc/apt/sources.list && \
    sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget -q https://dist.nuget.org/win-x86-commandline/latest/nuget.exe -O /usr/local/bin/nuget.exe

COPY Juleportal/ ./Juleportal/

WORKDIR /kilde/Juleportal

RUN mkdir -p pakker && \
    mono /usr/local/bin/nuget.exe install Newtonsoft.Json -Version 13.0.3 -OutputDirectory pakker && \
    mono /usr/local/bin/nuget.exe install System.Data.SQLite.Core -Version 1.0.118.0 -OutputDirectory pakker

RUN mcs -target:exe -out:Juleportal.exe \
    -r:System.dll \
    -r:System.Core.dll \
    -r:System.Data.dll \
    -r:System.Net.Http.dll \
    -r:System.Web.dll \
    -r:pakker/Newtonsoft.Json.13.0.3/lib/net45/Newtonsoft.Json.dll \
    -r:pakker/Stub.System.Data.SQLite.Core.NetFramework.1.0.118.0/lib/net46/System.Data.SQLite.dll \
    Program.cs \
    Modeller/Bruker.cs \
    Modeller/Sesjon.cs \
    Data/DatabaseKontekst.cs \
    Tjenester/SlumptallsgeneratorTjeneste.cs \
    Tjenester/Sesjonstjeneste.cs \
    Kontrollere/AutentiseringKontroller.cs \
    HttpTjener.cs

FROM alpine:latest

WORKDIR /app

RUN mkdir -p /tmp/runtime && chmod 700 /tmp/runtime

ENV XDG_RUNTIME_DIR=/tmp/runtime
ENV WINEDEBUG=-all

RUN apk update && apk add wine

RUN mkdir -p /usr/share/wine/mono && \
    wget -q https://dl.winehq.org/wine/wine-mono/10.3.0/wine-mono-10.3.0-x86.tar.xz -O /tmp/wine-mono.tar.xz && \
    tar -xf /tmp/wine-mono.tar.xz -C /usr/share/wine/mono && \
    rm /tmp/wine-mono.tar.xz && \
    ls -la /usr/share/wine/mono/

USER root

COPY --from=build /kilde/Juleportal/Juleportal.exe /app/
COPY --from=build /kilde/Juleportal/pakker/Newtonsoft.Json.13.0.3/lib/net45/Newtonsoft.Json.dll /app/
COPY --from=build /kilde/Juleportal/pakker/Stub.System.Data.SQLite.Core.NetFramework.1.0.118.0/lib/net46/System.Data.SQLite.dll /app/
COPY --from=build /kilde/Juleportal/pakker/Stub.System.Data.SQLite.Core.NetFramework.1.0.118.0/build/net46/x64/SQLite.Interop.dll /app/
COPY Juleportal/nettside/ /app/nettside/

RUN mkdir -p /data && chmod 777 /data

ENV DATABASE_STI=/data/juleportal.db
ENV NETTSIDE_STI=/app/nettside
ENV PORT=8080

EXPOSE 8080

RUN winecfg --set-defaults
CMD ["wine", "Juleportal.exe"]