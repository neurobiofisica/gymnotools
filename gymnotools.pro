TEMPLATE = subdirs
SUBDIRS = common commongui crosspat dsfmt dtcwpt features paramchooser recog singlefish slice spikes storms svm svmtool winview

commongui.depends = common
crosspat.depends = common
features.depends = common dtcwpt
paramchooser.depends = commongui
#recog.depends = common
#singlefish.depends = common svm dtcwpt
slice.depends = common dsfmt
#spikes.depends = common
storms.depends = common
svmtool.depends = common svm
winview.depends = commongui
