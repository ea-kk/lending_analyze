var dls=[];
var app=document.getElementById("app");
var timer=0;
function dl() {
    console.log(dls.length);
    if (dls.length) {
    //var a=dls.pop().href;console.log(a);window.open(a);
    dls.pop().click();
    }
    else {clearInterval(timer); timer=0; setTimeout(next_pg,10000);}
}
function do_dl() {
    var rows=app.firstElementChild.firstElementChild.children[1].children[1].firstElementChild.children[1].children[1].children;
    for (var i=0;i<rows.length;i++) {
        var a=rows[i].children[2].firstElementChild.children[1];
        dls.push(a);
    }
    timer = setInterval(dl, 3000);
}
function next_pg() {
    var next_but=app.firstElementChild.firstElementChild.children[1].children[2].lastElementChild;
    if (next_but.tagName=="A") {
        next_but.click();
        do_dl();
    }
}
do_dl();
