var interval_unit_field = document.getElementById("id_interval_unit");
interval_unit_field.addEventListener("change", display_on_weekly);
display_on_weekly();

function display_on_weekly() {
    var date_field_div = document.getElementsByClassName("field-starting_date")[0];
    if(interval_unit_field.value === "weeks"){
        date_field_div.style.display = "";
    }else{
        date_field_div.style.display = "none";
    }

}