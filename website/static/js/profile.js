const a = document.getElementById("act");
const div = document.getElementById("nw");

div.style.display = "none";
a.addEventListener("click", (event) => {
    if (div.style.display == "none") {
        div.style.display = "block"
        a.innerHTML = "Cancel";
    } else {
        div.style.display = "none"
        a.innerHTML = "Change Password";
    }
})