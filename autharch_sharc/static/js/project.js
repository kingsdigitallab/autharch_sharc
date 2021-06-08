$(document).ready(function () {

    // Return the text nodes of the context. Code by Mark Baijens from
    // https://stackoverflow.com/questions/4106809/how-can-i-change-an-elements-text-without-changing-its-child-elements/4106957
    jQuery.fn.textNodes = function () {
        return this.contents().filter(function () {
            return (this.nodeType === Node.TEXT_NODE);
        });
    };

    initAutocompleteWidgets();

    // SELECT-WITH-SEARCH
    // add search bar to the select dropdown
    $('.select-with-search').select2({
        placeholder: 'Select',
        allowClear: true
    });
    //add aria-label to select2 input
    $('.select2-search__field').attr('aria-label', 'select with search');
    $('.select2-selection__rendered').attr('aria-label', 'select2-selection__rendered');
    $('.select2-selection--multiple').attr({
        'aria-label': 'select2-selection--multiple',
        'role': 'list'
    });
    $('.select2-selection--single').attr({
        'role': 'list'
    });

    // TABLE PAGINATION / TABLESORTER
    if (!$('#duplicates-table [name="primary_record"]:checked').length) {
        $('.duplicate-cell').children('label').addClass("disabled");
    } else {
        $('#duplicates-table [name="primary_record"]:checked').each(function () {
            $(this).closest('.primary-cell').addClass('border-left');
            $(this).parent('label').addClass("selected");
            $(this).closest('.primary-cell').next('.duplicate-cell > label').addClass("disabled");
        })
    }


    $('#duplicates-table').on('click', '[name="primary_record"]', function (el) {
        //reset to default
        $('.primary-cell').removeClass('border-left');
        $('.primary-cell > label').removeClass("selected");
        $('.duplicate-cell').children('label').removeClass("disabled");
        $('.duplicate-cell').children('label').show();
        //update cells
        $(el.target).closest('.primary-cell').addClass('border-left');
        if ($(el.target).is(":checked")) {
            $(el.target).parent('label').addClass("selected");
            $(el.target).closest('.primary-cell').next('.duplicate-cell').find('input[type=radio]:checked').prop('checked', false);
            ;
            $(el.target).closest('.primary-cell').next('.duplicate-cell').children('label').addClass("disabled");
        }
    });

    // sorter for the archival records table - Collection -> Series -> File -> Item
    $.tablesorter.addParser({
        id: 'level',
        is: function (s) {
            return false;
        },
        format: function (s) {
            return s.toLowerCase()
                .replace("collection", "0")
                .replace("series", "1")
                .replace("file", "2")
                .replace("item", "3");
        },
        type: 'numeric'
    });


    $('.tablesorter').each(function (i, el) {

        $.tablesorter.customPagerControls({
            table: $('#' + $(el).attr('id')),                   // point at correct table (string or jQuery object)
            pager: $('#' + $(el).parent('.table-container').next('.pager').attr('id')),                   // pager wrapper (string or jQuery object)
            pageSize: '.page-size a',                // container for page sizes
            currentPage: '.page-list a',               // container for page selectors
            ends: 2,                        // number of pages to show of either end
            aroundCurrent: 1,                        // number of pages surrounding the current page
            link: '<a href="#" class="page">{page}</a>', // page element; use {page} to include the page number
            currentClass: 'current',                // current page class name
            adjacentSpacer: '',       // spacer for page numbers next to each other
            distanceSpacer: '<span> &#133; <span>',   // spacer for page numbers away from each other (ellipsis = &#133;)
            addKeyboard: true,                     // use left,right,up,down,pageUp,pageDown,home, or end to change current page
            pageKeyStep: 10                        // page step to use for pageUp and pageDown
        });


        //add tablesorter to the tables; had to go with an if-statement because tablesorter parameters cannot be modified once linked to a table
        if ($(el).attr('id') !== 'records-list-table') {
            /* $('#' + $(el).attr('id'))
                 .tablesorter({
                     widgets: ['filter'],
                     widgetOptions: {
                         filter_columnFilters: true,
                         filter_filterLabel: 'Filter records by {{label}}',
                     }
                 })*/
        } else {
            $('#records-list-table')
                .tablesorter({
                    widgets: ['filter'],
                    widgetOptions: {
                        filter_columnFilters: true,
                        filter_filterLabel: 'Filter records by {{label}}',

                    },
                    sortList: [[2, 0]],
                    headers: {
                        2: {
                            sorter: 'level'
                        }
                    }
                })
        }

        $('#' + $(el).attr('id')).tablesorterPager({
            container: $('#' + $(el).parent('.table-container').next('.pager').attr('id')),
            size: 10,
            // &paginate_by=&{filterList:filter}&{sortList:column}
            ajaxUrl: '/editor/records/?result_format=json&page={page+1}&paginate_by={size}',
            customAjaxUrl: function (table, url) {
                // Get the selected facets and q search
                let facet_link = $('#selected-facets').data('facet-link');
                if (facet_link && facet_link.length > 0){
                    url += '&' + facet_link;
                }
                return url;
            },
            ajaxObject: {
                type: 'GET', // default setting
                dataType: 'json'
            },
            processAjaxOnInit: false,
            savePages: false,
            pageReset: 0,
            ajaxProcessing: function (data) {
                console.log(data);
                var total_rows = data.count;
                var rows = [];
                var headers = [];
                if (data.results) {
                    var results = data.results;
                    for (var x = 0; x < results.length; x++) {
                        let row_title = results[x].title;
                        if (row_title.length > 100) {
                            row_title = row_title.substring(0, 100) + '...';
                        }
                        let row = [
                            '<a href="' + results[x].id + '/">' + row_title + "</a>",
                            results[x].category,
                            results[x].reference,
                            ''
                        ];
                        rows.push(row);

                    }
                }

                return [total_rows, rows, headers];
            }
        });

        //  make sure that corrent 'rows per page' number is active
        var rowsPerPage = $('#' + $(el).attr('id')).find('tbody > tr').filter(function () {
            return $(this).css('display') !== 'none';
        }).length;
        var label = 0;
        var rows = [10, 25, 50, 100];
        for (var i = 0; i < rows.length; i++) {
            if (rowsPerPage <= rows[i]) {
                label = rows[i];
                break;
            }
        }
        $("#" + $(el).attr('id')).parent('.table-container').next('.pager').find('a[data-label="' + label + '"]').addClass("current");
    });

    // close tooltips on click anywhere in the document
    $('form').on('click', function (e) {
        if (!$(e.target).is('.additional-info')) {
            if ($('.additional-info').length) {
                $('.additional-info').siblings('[role=button]').text("");
                $('.additional-info').remove();
            }
        }
    });


    //FILTERS
    // add clear all filters button when one of the facet options is selected
    if ($('.checkbox-anchor').children('input[type=checkbox]:checked').length > 0) {
        $('.clear-filters').addClass('active');
    } else {
        $('.clear-filters').removeClass('active');
    }
    // reduce the filter list size by adding the show all button
    $('.filter-list').each(function () {
        if ($(this).children("a").length > 5) {
            $(this).children("a").slice(5, $(this).children("a").length).hide();
            $(this).append(`<button class="button-link show-more" onclick="toggleFilters(this)"><i class="far fa-plus"></i> Show all (` + $(this).children("a").length + `)</button>`);
        }
    });
    // search in filter options and display options that match the query
    $('.instant-search').on('focus', function (e) {
        var filterOptions = $(e.target).siblings('.checkbox-anchor');
        $(e.target).on('keyup change', function () {
            var query = $(e.target).val().toLowerCase();
            if (query == '') {
                filterOptions.slice(0, 5).show();
                filterOptions.slice(6, filterOptions.length).hide();
                $(e.target).closest('fieldset').children('.show-more').remove();
                $(e.target).closest('fieldset').append(`<button class="button-link show-more" onclick="toggleFilters(this)"><i class="far fa-plus"></i> Show all (` + $(e.target).closest('fieldset').children("a").length + `)</button>`);
            } else {
                $(e.target).closest('fieldset').children('button.show-more').hide();
                filterOptions.each(function () {
                    var option = $(this).text().toLowerCase();
                    if (option.includes(query)) {
                        $(this).show();
                    } else {
                        $(this).hide();
                    }
                });
            }
        })
    });
    setUpYearSlider('creation');
    setUpYearSlider('acquisition');

    $('#duplicates-search-field').on('keyup change', function (e) {
        $('.fieldset-header').find('span').removeClass('greyed-out');
        $('div[class="series-level"]').children('.fieldset-body').removeClass('expand');
        $('.expand-collapse > button').text('Collapse all');
        $('.collections-level').removeClass('not-expanded')
        $('.fieldset-header').find('a.dotted-underline').each(function () {
            let option = $(this).text().toLowerCase();
            let query = $(e.target).val().toLowerCase();
            if (!option.includes(query)) {
                $(this).parents('.fieldset-header').first().find('span').addClass('greyed-out');
            } else {
                $(this).parents('div[class="series-level"]').find('.fieldset-body').addClass('expand');
            }
        });
    });

});

function exitHandler() {
    if (!document.fullscreenElement && !document.webkitIsFullScreen && !document.mozFullScreen && !document.msFullscreenElement) {
        var index = viewer.currentPage();
        $('#rte-pagination').pagination('selectPage', parseInt(index + 1));
    }
}

function showModal(modalName) {
    $('#' + modalName).addClass('active');
}

function hideModal() {
    $(event.target).parents('.modal').first().removeClass('active');
}

function removeNotification() {
    $(event.target).parent().remove();
}

// expand/collapse entity/archival record sections and individual sections on the hierarchy page
function toggleTab(el) {
    event.preventDefault();
    $(el).parents('.fieldset-header').siblings('.fieldset-body').toggleClass('expand');
    $(el).toggleClass('active');
}

// expand a hierarchical tree
function toggleExpand(el) {
    event.preventDefault();
    if ($('.collections-level').hasClass('not-expanded')) {
        $('.fieldset-body').addClass('expand');
        $('.toggle-tab-button').addClass('active');
        $(el).text('Collapse all');
    } else {
        $('.series-level').find('.fieldset-body').removeClass('expand');
        $('.series-level').find('.toggle-tab-button').removeClass('active');
        $(el).text('Expand all');
    }
    $('.collections-level').toggleClass('not-expanded');
}

function showAllMoreInformation(el) {
    $('[id^="checkbox_"]').prop('checked', !$('[id^="checkbox_"]').prop('checked'));
    if ($('[id^="checkbox_"]').prop('checked')) {
        $(el).text('Collapse all');
    } else {
        $(el).text('Expand all');
    }
}

// show more/less facet options
function toggleFilters(el) {
    event.preventDefault();
    var fieldset = $(el).parent('fieldset').first();
    $(fieldset).children('.show-more').remove();
    if ($(fieldset).children('a[style="display: none;"]').length) {
        $(fieldset).children('a').show();
        $(fieldset).append(`<button class="button-link show-more" onclick="toggleFilters(this)"><i class="far fa-minus"></i> Show less</button>`);
    } else {
        $(fieldset).children('a').slice(5, $(fieldset).children('a').length).hide();
        $(fieldset).append(`<button class="button-link show-more" onclick="toggleFilters(this)"><i class="far fa-plus"></i> Show all (` + $(fieldset).children("a").length + `)</button>`);
    }
}

// hide/show help text on single entity and archival records pages
function toggleHelpText(el, help_text) {
    event.stopPropagation();
    event.preventDefault();
    if ($(el).siblings('p.additional-info').length) {
        // change icon to 'question mark'
        $(el).text('');
        $(el).siblings('p.additional-info').remove();
    } else {
        var position = $(el).position();
        $(el).before('<p class="additional-info" style="top:' + (position.top - 40) + 'px; left:' + (position.left + 25) + 'px">' + help_text + '</p>');
        // change icon to 'close'
        $(el).text('');
    }
}

/**
 * Create confirmation modal dialogue with form to delete the current
 * record (whether Archival Record or Entity).
 */
function deleteRecord(event) {
    $('#delete-modal').addClass('active');
    event.preventDefault();
}

/**
 * Add a new empty form of the specified form_type.
 *
 * The blueprints for new forms are in div[@id='empty_forms'], and each
 * has a @data-form-type specifying the form_type.
 *
 * Updates the containing formset's management form controls and sets
 * the name and ids of the new form's controls to use the correct
 * prefix.
 *
 * The place where the new form is put, the location of the management
 * form's TOTAL_FORMS control that is edited, and the determination of
 * nested form's @id/@name prefix is based solely on the provided
 * context element; see {@link getManagementFormTotalControl} and
 * {@link getNewFormParent}.
 *
 * @param {string} formType - the type of form to add, corresponding to
 *                            the @data-form-type of the blueprint
 *                            empty form
 * @param {Element} context - the element from which the call to this
 *                            function was made
 */
function addEmptyForm(formType, context) {
    let jContext = $(context);
    let managementFormContainer = getManagementFormContainer(jContext);
    let maxNumControl = managementFormContainer.children('input[name$="MAX_NUM_FORMS"]');
    let maxNumForms = Number(maxNumControl.attr('value'))
    let totalControl = managementFormContainer.children('input[name$="TOTAL_FORMS"]');
    let newFormPrefixNumber = Number(totalControl.attr('value'));
    if ((newFormPrefixNumber + 1) >= maxNumControl.attr('value')) {
        $(jContext).parent('label').hide();
    }
    // Clone the formType form and add it as the last child of the
    // parent of these forms.
    let formParent = getNewFormParent(jContext);
    let newForm = $('#empty_forms').children('*[data-form-type=' + formType + ']').clone();
    newForm.appendTo(formParent);
    // Update the new form's controls' @name and @id to use the correct
    // values for its context in the hierarchy of formsets. Their prefix
    // (the part up to the end of the last "__prefix__") should be
    // replaced with the prefix generated from the TOTAL_FORMS control
    // of the containing formset's management form (plus the number of
    // this form), which conveniently already has the full prefix
    // hierarchy in it.
    let newControls = newForm.find('*[name*="__prefix__"]');
    let newFormPrefixName = generateNewFormPrefix(totalControl, 'name', newFormPrefixNumber);
    let newFormPrefixId = generateNewFormPrefix(totalControl, 'id', newFormPrefixNumber);
    let prefixLength = '__prefix__'.length;
    newControls.each(function (index) {
        $(this).attr('name', function (i, val) {
            return newFormPrefixName + val.slice(val.lastIndexOf('__prefix__') + prefixLength);
        });
        $(this).attr('id', function (i, val) {
            return newFormPrefixId + val.slice(val.lastIndexOf('__prefix__') + prefixLength);
        });
        if ($(this).hasClass('select-with-search-dynamic')) {
            $(this).select2({
                placeholder: 'Select',
                allowClear: true
            });
        }
        if ($(this).hasClass('richtext')) {
            tinymce.EditorManager.execCommand('mceAddEditor', true, $(this).attr('id'));
        }
    });
    // The management form for the formset of the new form must have its
    // TOTAL_FORMS value incremented by 1 to account for the new form.
    totalControl.attr('value', newFormPrefixNumber + 1);
    initAutocompleteWidgets();
}

/**
 * Return a string prefix for a new form whose TOTAL_FORMS control is
 * the supplied control, based on its attrName attribute value and the
 * prefixNumber.
 *
 * @param {jQuery} control - TOTAL_FORMS control
 * @param {String} attrName - name of control's attribute to use as the base
 * @param {Number} prefixNumber - number of the new form
 * @returns {String}
 */
function generateNewFormPrefix(control, attrName, prefixNumber) {
    let attrValue = control.attr(attrName);
    return attrValue.slice(0, attrValue.indexOf('TOTAL_FORMS')) + String(prefixNumber);
}


/**
 * Return the container for the Django formset's management form
 * controls associated with the supplied context element.
 *
 * This function is specific to a particular HTML structure, and
 * should be adapted if/when that structure changes.
 *
 * @param {jQuery} context - the element from which to traverse the
 *                           DOM to find the management form's container
 * @returns {jQuery}
 */
function getManagementFormContainer(context) {
    return context.parents('.formset').first().children('div.management_form');
}


/**
 * Return the jQuery object containing the element that is to be the
 * container for a new form.
 *
 * This function is specific to a particular HTML structure, and
 * should be adapted if/when that structure changes.
 *
 * @param {jQuery} context - the element from which to traverse the
 *                           DOM to find the parent for the new form
 * @returns {jQuery}
 */
function getNewFormParent(context) {
    return context.parents('.formset').first().children('div.fieldsets').last();
}


// this won't delete the field(s), just hide them. The deletion needs to be executed in the backend, once the form is submitted.
function deleteField(el, toDelete) {
    event.preventDefault();
    $(el).closest(toDelete).addClass('none');
    $(el).parents('.formset').first().children('label').show();
}


function deleteRow(el) {
    if (!$(el).parent().siblings('td').hasClass('none')) {
        $(el).parent().siblings('td').addClass('none');
        $(el).parent().attr('colspan', '6');
        $(el).after(`<span class="confirm-deletion"><i class="fas fa-trash-alt"></i><input name="all_users_submit" aria-label="save admin table" type="submit" class="button-link danger" value="Delete permanently and save table" /></span>`)
    } else {
        $(el).parent().attr('colspan', '1');
        $(el).parent().siblings('td').removeClass('none');
        $(el).siblings('.confirm-deletion').remove();
    }
    // Find and toggle the DELETE checkbox for the form.
    let deleteField = $(el).closest('[data-form-type]').find('[class~="delete-form-field"]').find('[name$="DELETE"]').first();
    deleteField.prop('checked', !deleteField.prop('checked'));
}


/**
 * Return the current URL's querystring with the prefix + "_start_year" and
 * prefix + "_end_year" parameters set to the supplied startYear and endYear.
 *
 * @param {String} prefix - prefix to use in parameter names
 * @param {Number} startYear - the year to set as start_year in the querystring
 * @param {Number} endYear - the year to set as end_year in the querystring
 * @returns {String}
 */
function generateYearURL(prefix, startYear, endYear) {
    let searchParams = new URLSearchParams(location.search);
    searchParams.set(prefix + '_start_year', startYear)
    searchParams.set(prefix + '_end_year', endYear)
    return '?' + searchParams.toString();
}


/**
 * Initialise all autocomplete widgets except ones in an empty
 * template form.
 *
 * Multiple initialisations of the same widgets does not appear to
 * cause problems.
 */
function initAutocompleteWidgets() {
    $('.autocomplete').not('[name*=__prefix__]').select2();
}


/**
 * Create and initialise a year slider, handling all of its various
 * updates to the "submit" link etc.
 */
function setUpYearSlider(prefix) {
    let startYearWidget = $('#id_' + prefix + '_start_year');
    let endYearWidget = $('#id_' + prefix + '_end_year');
    let sliderWidget = $('#' + prefix + '-year-range');
    let sliderAnchor = $('#' + prefix + '-year-range-anchor');

    let minValue = Number(startYearWidget.attr('min'));
    let maxValue = Number(endYearWidget.attr('max'));

    if (startYearWidget.val() == '') {
        startYearWidget.val(minValue);
    }
    if (endYearWidget.val() == '') {
        endYearWidget.val(maxValue);
    }

    let startYear = parseInt(startYearWidget.val());
    let endYear = parseInt(endYearWidget.val());
    let queryString = generateYearURL(prefix, startYear, endYear);

    sliderAnchor.attr('href', queryString);

    sliderWidget.slider({
        range: true,
        min: minValue,
        max: maxValue,
        values: [startYear, endYear],
        slide: function (event, ui) {
            let startYear = ui.values[0];
            let endYear = ui.values[1];
            let queryString = generateYearURL(prefix, startYear, endYear);
            startYearWidget.val(startYear);
            endYearWidget.val(endYear);
            sliderAnchor.attr('href', queryString);
        }
    });

    startYearWidget.on('keyup change', function (el) {
        let endYear = parseInt(endYearWidget.val());
        if ($(el.target).val() >= minValue && $(el.target).val() <= endYear) {
            sliderWidget.slider("values", 0, $(el.target).val());
            let queryString = generateYearURL(prefix, startYearWidget.val(),
                endYearWidget.val());
            sliderAnchor.attr('href', queryString);
        }
    });
    endYearWidget.on('keyup change', function (el) {
        let startYear = parseInt(startYearWidget.val());
        if ($(el.target).val() >= startYear && $(el.target).val() <= maxValue) {
            sliderWidget.slider('values', 1, $(el.target).val());
            let queryString = generateYearURL(prefix, startYearWidget.val(),
                endYearWidget.val());
            sliderAnchor.attr('href', queryString);
        }
    });
}


/**
 * Mark/unmark an inline form for deletion.
 *
 * This involves three changes:
 *
 * 1. Toggling the DELETE checkbox for the form.
 * 2. Toggling the visibility of the form.
 * 3. Toggling the delete/undo icon.
 *
 * This code requires the following HTML structure in order to behave
 * correctly:
 *
 * 1. The toggling instigator (the delete/undo icon) must be a
 * descendant of an element with the data-form-type attribute
 * set. This attribute marks the element that encompasses the whole of
 * an inline form.
 *
 * 2. The part of the form to be hidden/shown must have the class
 * attribute value "inline-deletable".
 *
 * 3. The part of the form to be hidden/shown must be a descendant of
 * the encompassing element (see #1).
 *
 * 4. The DELETE checkbox for the form must be a descendant (within an
 * element with a class of "inline-delete-form-field") of the part of
 * the form to be hidden/shown (see #2).
 *
 * @param {Element} button - the button element that triggered the toggle
 */
function toggleDeleteInline(event, button) {
    event.preventDefault();
    let jButton = $(button);
    let label = jButton.parent('label');
    let header = label.parents('.fieldset-header');
    let fieldset = header.parent('fieldset');

    // grey out the header if inactive
    header.toggleClass('inactive');
    // uncheck preferred identity
    header.find('input[type="checkbox"]:checked').prop('checked', false);
    fieldset.removeClass('border-left');
    // remove toggle button
    header.find('.toggle-tab-button').toggleClass('inactive');
    //toggle the display of preferred identity and authorised form
    header.find('input[type="checkbox"]').parent().toggleClass('none');

    // Find the element for the part of the form to be shown/hidden,
    // and toggle its visibility.
    let form_part = jButton.closest('[data-form-type]').find('[class~="inline-deletable"]').first();
    form_part.toggleClass('none');

    // toggle the checkbox button and text label
    if (form_part.hasClass('none')) {
        jButton.val('');
        label.removeClass('danger');
        label.addClass('save');
        label.append(`<span>Undo</span>`);
        label.parent().after(`<button class="button-link danger" onclick="deleteField(this, '[data-form-type]')"><i class="fas fa-trash-alt"></i>Delete permanently</button>`)
    } else {
        jButton.val('');
        label.removeClass('save');
        label.addClass('danger');
        label.children('span').remove();
        label.parent().siblings('button.danger').remove();
    }

    // Find and toggle the DELETE checkbox for the form.
    let deleteField = form_part.children('[class~="inline-delete-form-field"]').find('[name$="DELETE"]').first();
    deleteField.prop('checked', !deleteField.prop('checked'));
}


/**
 * Set/remove the required attribute of the supplied form controls.
 *
 * @param {jQuery} controls - controls to manipulate
 * @param {Boolean} add_required - whether to add (true) or remove the
 *                                 required attribute
 */
function toggleRequiredControls(controls, add_required) {
    let value = null;
    if (add_required) {
        value = 'required';
    }
    controls.attr('required', value);
}
