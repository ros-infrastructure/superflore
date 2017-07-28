FROM gentoo/stage3-amd64


RUN emerge-webrsync && emerge --sync && emerge app-crypt/gnupg repoman dev-vcs/git

ENV FEATURES sign
ENV PORTAGE_GPG_DIR ~/.gnupg/

RUN mkdir -p /usr/local/portage
RUN printf '\nPORTDIR_OVERLAY="/usr/local/portage"' >> /etc/portage/make.conf
