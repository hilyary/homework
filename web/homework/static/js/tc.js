// 获取弹窗和关闭按钮的元素
var modal = document.getElementById("myModal");
var closeBtn = document.getElementsByClassName("close")[0];

// 当用户点击关闭按钮时，隐藏弹窗
closeBtn.onclick = function() {
  modal.style.display = "none";
};

// 当用户点击除弹窗外的其他地方时，隐藏弹窗
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

// 当用户点击打开弹窗的按钮时，显示弹窗
document.getElementById("myBtn").onclick = function() {
    modal.style.display = "block";
  };