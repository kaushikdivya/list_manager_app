/**
*/
/*
$(function() {
    $('input:checkbox').on('change', function(e) {

        var radio = $(this).parent('.radio');

        if (this.checked){
            radio.find('input:text').css('textDecoration', 'line-through')
            radio.find('.edit_btn').removeClass("btn-success").addClass("checked_checkbox").prop("disabled", true)
        } else {
            radio.find('input:text').css('textDecoration', 'none')
            radio.find('.edit_btn').removeClass("btn-danger checked_checkbox disabled").addClass("btn-success").prop("disabled", false)
        }
    });

    $('input:text').on('click', function(e) {

        label = $(this)
        label.hide();

        var labelText = label.val();

        label.after("<input type='text' value='" + labelText + "' />");

        var input = label.next();
        input.focus();
        var saveButton = input.next();
        saveButton.click(function () {
            labelText = input.val();
            label.text(labelText);
            input.remove();
            $(this).remove();
            label.show();
        });
    });
});
*/
