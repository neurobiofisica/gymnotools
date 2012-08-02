TEMPLATE = subdirs
SUBDIRS = common commongui dsfmt dtcwpt features paramchooser slice spikes svm svmtool winview

commongui.depends = common
features.depends = common dtcwpt
paramchooser.depends = commongui
slice.depends = common dsfmt
spikes.depends = common
svmtool.depends = common svm
winview.depends = commongui
