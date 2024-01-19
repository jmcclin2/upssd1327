local sprite = app.activeSprite

-- Check constraints
if sprite == nil then
  app.alert("No Sprite...")
  return
end
if sprite.colorMode ~= ColorMode.INDEXED then
  app.alert("Sprite needs to be indexed")
  return
end

local function getPaletteData(palette)
	local ncolors = #palette
	local res = string.format("%i\n", ncolors)

	for i=0, ncolors-1 do
		local color = palette:getColor(i)
		res = res .. string.format("%i %i %i %i\n", color.red, color.green, color.blue, color.alpha)		
	end

	return res
end

local function getIndexData(img, x, y, w, h)
	local res = ""
	for y = 0,h-1 do
		for x = 0, w-1, 2 do
			
			if x == 0 then
				res = res .. string.format("%s", "b'")
			end		

			px1 = img:getPixel(x, y)
			px2 = img:getPixel(x+1, y)
			res = res .. string.format("\\x%1X%1X", px1, px2)
			
			if x+1 == w-1 then
				res = res .. string.format("\'\\")
			end
		end
		res = res .. "\n"
	end

	return res
end

local function getBytesVariableName()
	local dlg = Dialog()
	dlg:entry{ id="user_value", label="Bytes variable name:", text="sprite" }
	dlg:button{ id="ok", text="OK" }
	dlg:show()
	local data = dlg.data
	return data.user_value
end

local function exportFrame(frm)
	if frm == nil then
		frm = 1
	end

	local img = Image(sprite.spec)
	img:drawSprite(sprite, frm)

	io.write("_data =\\\n")
	io.write(getIndexData(img, x, y, sprite.width, sprite.height))
	io.write("\n_mvdata = memoryview(_data)\n\n")
	io.write("def data():\n")
	io.write("    return _mvdata\n")
end


local dlg = Dialog()
dlg:file{ id="exportFile",
          label="File",
          title="4-Bit Python Image Export",
          open=false,
          save=true,
          filetypes={ "py" }}
dlg:check{ id="onlyCurrentFrame",
           text="Export only current frame",
           selected=true }

dlg:button{ id="ok", text="OK" }
dlg:button{ id="cancel", text="Cancel" }
dlg:show()
local data = dlg.data
if data.ok then
	local f = io.open(data.exportFile, "w")
	io.output(f)

	if data.onlyCurrentFrame then
		exportFrame(app.activeFrame)
	else
	 	for i = 1,#sprite.frames do
	 		io.write(string.format(";Frame %d\n", i))
	 		exportFrame(i)
		end
	end

	io.close(f)
end