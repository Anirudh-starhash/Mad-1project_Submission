const pass=document.getElementById("pass2")
const conpass=document.getElementById("conpass2")

function validate(e){
    if(pass.value!=conpass.value){
        alert('Confirm password and password are not same')
        return false
    }
}