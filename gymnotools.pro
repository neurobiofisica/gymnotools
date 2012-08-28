TEMPLATE = subdirs
SUBDIRS = common commongui dsfmt dtcwpt features paramchooser singlefish slice spikes storms svm svmtool winview

commongui.depends = common
features.depends = common dtcwpt
paramchooser.depends = commongui
singlefish.depends = common svm dtcwpt
slice.depends = common dsfmt
spikes.depends = common
storms.depends = common
svmtool.depends = common svm
winview.depends = commongui
