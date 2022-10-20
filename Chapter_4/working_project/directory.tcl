#############################################################################
# Generated by PAGE version 6.2
#  in conjunction with Tcl version 8.6
#  Nov 01, 2021 02:36:42 PM CET  platform: Linux
set vTcl(timestamp) ""
if {![info exists vTcl(borrow)]} {
    tk_messageBox -title Error -message  "You must open project files from within PAGE."
    exit}


set image_list { \
    icon_arrowbutton_gif "../working_project/images/icon_arrowbutton.gif" \
    map_png "../working_project/images/map.png" \
}
vTcl:create_project_images $image_list   ;# In image.tcl


if {!$vTcl(borrow) && !$vTcl(template)} {

set vTcl(actual_gui_font_dft_desc)  TkDefaultFont
set vTcl(actual_gui_font_dft_name)  TkDefaultFont
set vTcl(actual_gui_font_text_desc)  TkTextFont
set vTcl(actual_gui_font_text_name)  TkTextFont
set vTcl(actual_gui_font_fixed_desc)  TkFixedFont
set vTcl(actual_gui_font_fixed_name)  TkFixedFont
set vTcl(actual_gui_font_menu_desc)  TkMenuFont
set vTcl(actual_gui_font_menu_name)  TkMenuFont
set vTcl(actual_gui_font_tooltip_desc)  TkDefaultFont
set vTcl(actual_gui_font_tooltip_name)  TkDefaultFont
set vTcl(actual_gui_font_treeview_desc)  TkDefaultFont
set vTcl(actual_gui_font_treeview_name)  TkDefaultFont
set vTcl(actual_gui_bg) #d9d9d9
set vTcl(actual_gui_fg) #000000
set vTcl(actual_gui_analog) #ececec
set vTcl(actual_gui_menu_analog) #ececec
set vTcl(actual_gui_menu_bg) #d9d9d9
set vTcl(actual_gui_menu_fg) #000000
set vTcl(complement_color) #d9d9d9
set vTcl(analog_color_p) #d9d9d9
set vTcl(analog_color_m) #ececec
set vTcl(active_fg) #000000
set vTcl(actual_gui_menu_active_bg)  #ececec
set vTcl(actual_gui_menu_active_fg)  #000000
set vTcl(pr,autoalias) 1
set vTcl(pr,relative_placement) 1
set vTcl(mode) Relative
}




proc vTclWindow.top45 {base} {
    global vTcl
    if {$base == ""} {
        set base .top45
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -background $vTcl(actual_gui_bg) 
    wm focusmodel $top passive
    wm geometry $top 1280x720+183+207
    update
    # set in toplevel.wgt.
    global vTcl
    global img_list
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 1905 1050
    wm minsize $top 1 1
    wm overrideredirect $top 0
    wm resizable $top 0 0
    wm deiconify $top
    wm title $top "Directory"
    vTcl:DefineAlias "$top" "Directory" vTcl:Toplevel:WidgetProc "" 1
    set vTcl(real_top) {}
    vTcl:withBusyCursor {
    label $top.lab47 \
        -background $vTcl(actual_gui_bg) -foreground $vTcl(actual_gui_fg) \
        -image map_png -text Label 
    vTcl:DefineAlias "$top.lab47" "map" vTcl:WidgetProc "Directory" 1
    button $top.but48 \
        -background $vTcl(actual_gui_bg) -borderwidth 2 \
        -foreground $vTcl(actual_gui_fg) -highlightcolor black \
        -image icon_arrowbutton_gif -text Button 
    vTcl:DefineAlias "$top.but48" "target_button" vTcl:WidgetProc "Directory" 1
    button $top.but49 \
        -activebackground #f9f9f9 -activeforeground black \
        -background $vTcl(actual_gui_bg) -borderwidth 2 \
        -foreground $vTcl(actual_gui_fg) -highlightcolor black \
        -image icon_arrowbutton_gif -text Button 
    vTcl:DefineAlias "$top.but49" "sears_button" vTcl:WidgetProc "Directory" 1
    button $top.but50 \
        -activebackground #f9f9f9 -activeforeground black \
        -background $vTcl(actual_gui_bg) -borderwidth 2 \
        -foreground $vTcl(actual_gui_fg) -highlightcolor black \
        -image icon_arrowbutton_gif -text Button 
    vTcl:DefineAlias "$top.but50" "zara_button" vTcl:WidgetProc "Directory" 1
    label $top.lab51 \
        -background $vTcl(actual_gui_bg) -foreground $vTcl(actual_gui_fg) \
        -text Label 
    vTcl:DefineAlias "$top.lab51" "description_label" vTcl:WidgetProc "Directory" 1
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.lab47 \
        -in $top -x 0 -y 0 -width 0 -relwidth 1 -height 0 -relheight 1 \
        -anchor nw -bordermode ignore 
    place $top.but48 \
        -in $top -x 0 -relx 0.453 -y 0 -rely 0.306 -width 20 -relwidth 0 \
        -height 19 -relheight 0 -anchor nw -bordermode ignore 
    place $top.but49 \
        -in $top -x 0 -relx 0.438 -y 0 -rely 0.722 -width 20 -relwidth 0 \
        -height 19 -relheight 0 -anchor nw -bordermode ignore 
    place $top.but50 \
        -in $top -x 0 -relx 0.914 -y 0 -rely 0.389 -width 20 -relwidth 0 \
        -height 19 -relheight 0 -anchor nw -bordermode ignore 
    place $top.lab51 \
        -in $top -x 0 -relx 0.445 -y 0 -rely 0.361 -width 0 -relwidth 0.03 \
        -height 0 -relheight 0.021 -anchor nw -bordermode ignore 
    } ;# end vTcl:withBusyCursor 

    vTcl:FireEvent $base <<Ready>>
}



set btop ""
if {$vTcl(borrow)} {
    set btop .bor[expr int([expr rand() * 100])]
    while {[lsearch $btop $vTcl(tops)] != -1} {
        set btop .bor[expr int([expr rand() * 100])]
    }
}
set vTcl(btop) $btop
Window show .
Window show .top45 $btop
if {$vTcl(borrow)} {
    $btop configure -background plum
}

