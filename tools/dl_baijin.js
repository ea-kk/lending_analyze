var dls=[];
var app=document.getElementById("app");
var rows=app.firstElementChild.firstElementChild.children[1].children[1].firstElementChild.children[1].children[1].children;
var timer=0;
function dl() {
    console.log(dls.length);
    if (dls.length) {
    //var a=dls.pop().href;console.log(a);window.open(a);
    dls.pop().click();
    }
    else {clearInterval(timer); timer=0;}
}
function do_dl() {
    for (var i=0;i<rows.length;i++) {
        var a=rows[i].children[2].firstElementChild.children[1];
        dls.push(a);
    }
    timer = setInterval(dl, 2000);
}

do_dl();
