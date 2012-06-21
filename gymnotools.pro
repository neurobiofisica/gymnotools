TEMPLATE = subdirs
SUBDIRS = common commongui dsfmt dtcwpt paramchooser spikes svm

commongui.depends = common
paramchooser.depends = commongui
spikes.depends = common
