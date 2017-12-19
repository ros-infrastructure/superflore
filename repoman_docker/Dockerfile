FROM gentoo/stage3-amd64

RUN mkdir -p /usr/portage/gentoo && emerge-webrsync && emerge --sync \
    && eselect profile set 12 && emerge app-crypt/gnupg repoman dev-vcs/git --autounmask-write

ENV FEATURES sign
ENV PORTAGE_GPG_DIR ~/.gnupg/

RUN mkdir -p /usr/local/portage
RUN printf '\nPORTDIR_OVERLAY="/usr/local/portage"' >> /etc/portage/make.conf
