/**
*/
var my_func = function() {

    /*$(document).on('click', '.btn-add', function(e) {
        e.preventDefault();
        var controlForm = $('.controls form:first'),
            controlsFormItemList = $('.controlsFormItemList'),
            currentEntry = $(this).parents('.entry:first'),
            newEntry = $(currentEntry.clone()).prependTo(controlsFormItemList);

        newEntry.find('input').val($('#fields').val());
        controlForm.find('.entry:not(:first) .btn-add')
            .removeClass('btn-add').addClass('btn-remove')
            .removeClass('btn-success').addClass('btn-danger')
            .html('<span class="glyphicon glyphicon-minus"></span>');
    });*/

    /*$(document).on('click', '.btn-remove', function(e) {
		$(this).parents('.entry:last').remove();
		e.preventDefault();
		return false;
	});*/

    $(document).on('click', '.add-new-item-button', function(e) {
        e.preventDefault();
        var itemsList = $('.items-list');
        var newItemHtml =
            "<div class=\"row\"> " +
                "<div class=\"list-item\"> " +
                    "<div class=\"form-group\"> " +
                        "<div class=\"radio\"> " +
                            "<input class=\"check\" type=\"checkbox\" name=\"check\" > " +
                            "<input type=\"hidden\" name=\"item_id\" value=\"\"> " +
                            "<input type=\"hidden\" name=\"status\" value=\"incomplete\"> " +
                            "<input type=\"text\" class=\"form-control check_label\" name=\"fields\" placeholder=\"item name\"> " +
                            "<input type=\"text\" class=\"form-control check_label\" name=\"quantity\" placeholder=\"quantity\"> " +
                            "<button type=\"button\" class=\"btn btn-default trash_btn\" name=\"trash_btn\"> " +
                                "<span class=\"glyphicon glyphicon-trash\"></span> " +
                            "</button> " +
                            "<br> " +
                        "</div> " +
                    "</div> " +
                "</div> " +
            "</div> ";
        // console.log('newItemHtml = ' + newItemHtml);
        var newItemHtmlElement = $($.parseHTML(newItemHtml));
        // console.log('newItemHtmlElement = ' + newItemHtmlElement);
        newItemHtmlElement.prependTo(itemsList);
    });

    $(document).on('change', 'input:checkbox', function(e) {
        var checkBoxes = $(this);

        var radio = $(this).parent('.radio');
        console.log($(this))

        if (this.checked) {
            radio.find('input:text').css('textDecoration', 'line-through');
            radio.find('input[name="status"]').attr("value", "complete");
            // radio.find('input').removeClass('unchecked').addClass('checked');
            // // $(this).parent('.radio').find('input[name="fields"]').addClass('checked');
            // // $(this).parent('.radio').find('input[name="quantity"]').addClass('checked');
            // $('input:not(.checked)').attr("disabled","disabled")
            // $(this).parents().eq(5).submit();
            // console.log($(this).parents().eq(5))
        } else {
            radio.find('input:text').css('textDecoration', 'none');
            radio.find('input[name="status"]').attr("value", "incomplete");
            radio.find('input[name="fields"]').removeAttr("disabled");
            radio.find('input[name="quantity"]').removeAttr("disabled");
            // radio.find('input').addClass('unchecked').removeClass('checked');
            // $('input:not(.unchecked)').attr("disabled","disabled")
            // $(this).parents().eq(5).submit();
            // console.log($(this).parents().eq(5))
        }
    });

    $(document).on('click', 'button[name=trash_btn]', function(e) {
        var path = window.location.pathname;
        list_id = path.split('/')[2]
        console.log(list_id)
        $(this).parent('.radio').find('input').addClass('delete');
        $('input:not(.delete)').attr("disabled", "disabled")
        $(this).parents().eq(5).attr("action", "/lists/"+list_id+"/items/delete").submit();

        //$(this).parents().eq(5).submit();

    });

};

$(my_func);
