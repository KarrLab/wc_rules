Creator	"yFiles"
Version	"2.14"
graph
[
	hierarchic	1
	label	""
	directed	1
	node
	[
		id	0
		label	"(0) root"
		graphics
		[
			x	0.0
			y	0.0
			w	30.0
			h	30.0
			type	"ellipse"
			raisedBorder	0
			hasFill	0
			outline	"#000000"
		]
		LabelGraphics
		[
			text	"(0) root"
			fontSize	12
			fontName	"Dialog"
			model	"sides"
			anchor	"e"
		]
	]
	node
	[
		id	1
		label	"(1) is type Entity"
		graphics
		[
			x	0.0
			y	0.0
			w	30.0
			h	30.0
			type	"ellipse"
			raisedBorder	0
			hasFill	0
			outline	"#000000"
		]
		LabelGraphics
		[
			text	"(1) is type Entity"
			fontSize	12
			fontName	"Dialog"
			model	"sides"
			anchor	"e"
		]
	]
	node
	[
		id	2
		label	"(2) is type Molecule"
		graphics
		[
			x	0.0
			y	0.0
			w	30.0
			h	30.0
			type	"ellipse"
			raisedBorder	0
			hasFill	0
			outline	"#000000"
		]
		LabelGraphics
		[
			text	"(2) is type Molecule"
			fontSize	12
			fontName	"Dialog"
			model	"sides"
			anchor	"e"
		]
	]
	node
	[
		id	3
		label	"(3) is type A"
		graphics
		[
			x	0.0
			y	0.0
			w	30.0
			h	30.0
			type	"ellipse"
			raisedBorder	0
			hasFill	0
			outline	"#000000"
		]
		LabelGraphics
		[
			text	"(3) is type A"
			fontSize	12
			fontName	"Dialog"
			model	"sides"
			anchor	"e"
		]
	]
	node
	[
		id	4
		label	"(4) is type Site"
		graphics
		[
			x	0.0
			y	0.0
			w	30.0
			h	30.0
			type	"ellipse"
			raisedBorder	0
			hasFill	0
			outline	"#000000"
		]
		LabelGraphics
		[
			text	"(4) is type Site"
			fontSize	12
			fontName	"Dialog"
			model	"sides"
			anchor	"e"
		]
	]
	node
	[
		id	5
		label	"(5) is type X"
		graphics
		[
			x	0.0
			y	0.0
			w	30.0
			h	30.0
			type	"ellipse"
			raisedBorder	0
			hasFill	0
			outline	"#000000"
		]
		LabelGraphics
		[
			text	"(5) is type X"
			fontSize	12
			fontName	"Dialog"
			model	"sides"
			anchor	"e"
		]
	]
	edge
	[
		source	0
		target	1
		graphics
		[
			fill	"#000000"
			targetArrow	"standard"
		]
	]
	edge
	[
		source	1
		target	2
		graphics
		[
			fill	"#000000"
			targetArrow	"standard"
		]
	]
	edge
	[
		source	1
		target	4
		graphics
		[
			fill	"#000000"
			targetArrow	"standard"
		]
	]
	edge
	[
		source	2
		target	3
		graphics
		[
			fill	"#000000"
			targetArrow	"standard"
		]
	]
	edge
	[
		source	4
		target	5
		graphics
		[
			fill	"#000000"
			targetArrow	"standard"
		]
	]
]
