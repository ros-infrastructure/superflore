FROM gentoo/stage3-amd64

RUN mkdir -p /usr/portage/gentoo && emerge-webrsync && emerge --sync \
    && eselect profile set 12 && emerge app-crypt/gnupg repoman dev-vcs/git --autounmask-write

ENV FEATURES sign
ENV PORTAGE_GPG_DIR ~/.gnupg/

RUN mkdir -p /usr/local/portage
RUN printf '\nPORTDIR_OVERLAY="/usr/local/portage"\n' >> /etc/portage/make.conf

RUN mkdir /etc/portage/repos.conf
RUN echo "[ros-overlay]" > /etc/portage/repos.conf/ros-overlay.conf &&\
    echo "location = /usr/local/portage" >> /etc/portage/repos.conf/ros-overlay.conf && \
    echo "sync-type = git" >> /etc/portage/repos.conf/ros-overlay.conf && \
    echo "sync-uri = https://github.com/ros/ros-overlay" >> /etc/portage/repos.conf/ros-overlay.conf && \
    echo "auto-sync = yes" >> /etc/portage/repos.conf/ros-overlay.conf && \
    echo "masters = gentoo" >> /etc/portage/repos.conf/ros-overlay.conf && \
    echo 'ACCEPT_KEYWORDS=~amd64' >> /etc/portage/make.conf && \
    printf 'USE="X -bindist"\n' >> /etc/portage/make.conf && \
    eselect profile set default/linux/amd64/17.0/desktop && \
    emaint sync -r ros-overlay && \
    emerge --oneshot portage && \
    echo "ros-*/* PYTHON_TARGETS: -* python2_7" >> /etc/portage/package.use/iputils && \
    echo "ros-*/* PYTHON_SINGLE_TAGET: *- python2_7" >> /etc/portage/package.use/iputils && \
    perl-cleaner --reallyall
RUN emerge -C openssl && \
    emerge openssl && \
    emerge dev-libs/boost && \
    emerge dev-util/cmake
