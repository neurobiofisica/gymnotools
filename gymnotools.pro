TEMPLATE = subdirs
SUBDIRS = common commongui dsfmt dtcwpt paramchooser spikes spkview svm

commongui.depends = common
paramchooser.depends = commongui
spikes.depends = common
spkview.depends = commongui
