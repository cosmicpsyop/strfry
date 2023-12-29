# Build stage
FROM fedora:39 as build
ENV TZ=Europe/London
WORKDIR /build

# Install build dependencies
RUN dnf update -y && dnf install -y autogen git g++ make rpmdevtools rpm-build pkg-config libtool ca-certificates \
        openssl-devel libzstd-devel lmdb-devel zlib-devel flatbuffers-devel flatbuffers-compiler \
        perl-YAML perl-Template-Toolkit perl-Regexp-Grammars

# Copy source code
COPY . .

# Clone secp256k1 repository
RUN git clone https://github.com/bitcoin-core/secp256k1.git

# Build secp256k1
RUN cd secp256k1 && ./autogen.sh && ./configure --enable-module-schnorrsig && make && make install

# Continue with the rest of the build steps
RUN git submodule update --init
RUN make setup-golpe
RUN make clean
RUN rpmbuild -bb --debug rpmbuild/SPECS/strfry.spec

# Final stage
FROM fedora:39 as runner
WORKDIR /app

# Copy only necessary artifacts from the build stage
COPY --from=build /build/strfry strfry
COPY --from=build /usr/local/lib/. /usr/local/lib/
COPY --from=build /root/rpmbuild/RPMS/x86_64/strfry-0.9.6-1.fc39.x86_64.rpm .


# Install minimal runtime dependencies
RUN dnf install -y lmdb-libs flatbuffers libzstd libb2
ENV LD_LIBRARY_PATH=/usr/local/lib

ENTRYPOINT ["/app/strfry"]
CMD ["relay"]

