FROM gentoo/stage3-amd64


RUN emerge-webrsync && emerge --sync && emerge app-crypt/gnupg repoman

ENV FEATURES sign
ENV PORTAGE_GPG_DIR ~/.gnupg/

RUN echo '\nPORTDIR_OVERLAY="/usr/local/portage"\nPORTDIR=/usr/portage' >> /etc/portage/make.conf
