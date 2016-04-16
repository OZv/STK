function p(n){
var d=parseFloat(n);
var c=d<0?"czx":(d==0?"psz":"yuv");
return '<span class="'+c+'">'+d.toFixed(2)+'%</span>';
}
function j(v,n){
var h="",t;
for(var i=2;i<v.length;i+=2){
if(v[i]==0)
h+='<td class="ukr">--</td>';
else{
t=(n==i/2-1)?"":' title="'+v[i+1]+'"';
h+='<td class="jyn"'+t+'>'+p(v[i])+"</td>";
}
}
return h;
}
function u(a,m){
if(a.className==m)return false;
var l=a.parentNode.childNodes;
for(var i=0;i<l.length;i++)
l[i].removeAttribute("class");
a.className=m;
return true;
}
function e8c(a,n){
var b=document.getElementById("tb8").childNodes[n];
if(!u(b,"oxc")&&a)return;
b=document.getElementsByTagName("tbody")[0];
var x=parseInt(b.getAttribute("data-index"),10);
var h="",c,e,k;
for(var i=0;i<vo[x][n].length;i++){
c=vo[x][n][i];
//console.info(c);
k=cl[c];
e=c.substr(0,1)=="6"?"SH":"SZ";
h+='<tr><td>'+(i+1)+'</td><td><a href="http://gupiao.baidu.com/stock/'+e.toLowerCase()+c+'.html" target="_blank">'+c+'</a></td><td><a href="http://www.windin.com/home/stock/html/'+c+'.'+e+'.shtml" target="_blank">'+k[0]+'</a></td><td class="jyn">'+p(vc[c][0])+"</td><td align=right>"+parseFloat(vc[c][1]).toFixed(2)+"</td>"+j(vc[c],n)+"<td>"+k[1]+"</td><td>"+k[2]+"</td></tr>";
}
b.innerHTML=h;
}
function g6z(){
var q=qg["quotation"],a,h="",c;
for(var i=0;i<q.length;i++){
a=q[i].split(",");
if(a[11].substr(0,1)=="-")c='"ixm"'; else c='"ixp"';
h+='<span class="qgi">'+a[2]+'</span><span class='+c+'>'+a[5]+'</span><span class='+c+'>'+a[11]+'</span>';
}
console.info(h);
var w=document.createElement("div");
w.className="qgd";
w.innerHTML=h;
var u=document.getElementsByTagName("div");
for(var i=0;i<u.length;i++)
if(u[i].className=="l7s"){
u[i].parentNode.insertBefore(w,u[i]);
break;
}
}
function k9y(a,n){
if(a&&!u(a,"nwl"))return;
if(!a){
var s=document.createElement("script");
s.setAttribute("src","http://hq2gjgp.eastmoney.com/EM_Quote2010NumericApplication/Index.aspx?reference=rtj&Type=Z&jsName=qg&ids=INDU7,CCMP7,NKY7");
s.setAttribute("onload","g6z()");
document.getElementsByTagName("head")[0].appendChild(s);
}
var b=document.getElementsByTagName("tbody")[0];
b.setAttribute("data-index",n);
e8c(null,0);
}
function d(){
k9y(null,0);
}
if(window.addEventListener)
window.addEventListener("load",d,false);
else window.attachEvent("onload",d);
