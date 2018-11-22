import 'jquery-ui-bundle';
import './widget.scss'
import setupWidget from '@pytsite/widget';
import $ from 'jquery';
import {lang} from '@pytsite/assetman';
import httpApi from '@pytsite/http-api';

setupWidget('plugins.file_ui._widget.FilesUpload', widget => {
    const widgetEm = widget.em;
    const slotsEm = widgetEm.find('.slots');
    const widgetUid = widgetEm.data('uid');
    const addBtn = widgetEm.find('.add-button');
    const postUrl = widgetEm.data('url');
    const maxFiles = parseInt(widgetEm.data('maxFiles'));
    const maxFileSizeMB = parseInt(widgetEm.data('maxFileSize'));
    const maxFileSize = maxFileSizeMB * 1048576;
    const fileInput = widgetEm.find('input[type=file]');
    const progressSlot = widgetEm.find('.progress');
    const progressBar = progressSlot.find('.progress-bar');
    const slotCss = widgetEm.data('slotCss');
    const showNumbers = widgetEm.data('showNumbers') === 'True';
    const dnd = widgetEm.data('dnd') === 'True';
    const previewImages = widgetEm.data('previewImages') === 'True';
    const thumbWidth = widgetEm.data('thumbWidth');
    const thumbHeight = widgetEm.data('thumbHeight');
    let filesCount = 0;
    let acceptedFileTypes = fileInput.prop('accept');

    if (acceptedFileTypes !== '*/*')
        acceptedFileTypes = acceptedFileTypes.split('/')[0];

    function sortableSetup() {
        if (!dnd)
            return;

        if (slotsEm.hasClass('ui-sortable')) {
            slotsEm.sortable('refresh');
        }
        else {
            slotsEm.sortable({
                containment: 'parent',
                cursor: 'move',
                revert: true,
                tolerance: 'pointer',
                items: '> .slot.sortable',
                forcePlaceholderSize: true,
                placeholder: 'slot placeholder ' + slotCss,
                update: renumberSlots
            });
        }
    }

    function setupSlot(slot) {
        // 'Remove' button click event handler
        $(slot).find('.btn-remove').click(function () {
            removeSlot(slot)
        });

        return $(slot);
    }

    function createSlot(uid, fileUrl, thumbUrl, fileName) {
        var slot = $('<div class="slot slot-content sortable ' + slotCss + '" data-uid="' + uid + '">');
        var inner = $('<div class="inner">');
        var actions = $('<div class="actions">');

        slot.append(inner);

        inner.append($('<div class="thumb" style="background-image: url(' + thumbUrl + ')"><img class="img-responsive img-fluid" src="' + thumbUrl + '" title="' + fileName + '"></div>'));
        inner.append('<input type="hidden" name="' + widgetUid + '[]" value="' + uid + '">');

        inner.append(actions);
        if (showNumbers) {
            actions.append($('<span class="number">'));
            actions.append($('<span class="spacer">'));
        }
        actions.append($('<a href="' + fileUrl + '" target="_blank" class="btn btn-default btn-light btn-sm btn-download" title="' + lang.t('plugins.file_ui@download_file') + '"><i class="fa fas fa-fw fa-download"></i></a>'));
        actions.append($('<button type="button" class="btn btn-danger btn-sm btn-remove" title="' + lang.t('plugins.file_ui@remove_file') + '"><i class="fa fas fa-fw fa-remove fa-times"></i></button>'));

        return setupSlot(slot);
    }

    function renumberSlots() {
        var n = 1;
        filesCount = 0;
        widgetEm.find('.slot-content').each(function () {
            if (showNumbers)
                $(this).find('.number').text(n++);

            ++filesCount;
        });

        if (filesCount >= maxFiles) {
            addBtn.css('display', 'none');
            widgetEm.addClass('max-files-reached');
        }
        else {
            addBtn.css('display', 'flex');
            widgetEm.removeClass('max-files-reached');
        }
    }

    function appendSlot(slot) {
        slotsEm.append(slot);
        progressSlot.insertAfter(slotsEm.find('.slot:last-child'));
        addBtn.insertAfter(slotsEm.find('.slot:last-child'));

        renumberSlots();
        sortableSetup();
    }

    function removeSlot(slot, confirmDelete) {
        var uid = $(slot).data('uid');

        if (confirmDelete !== false && !confirm(lang.t('plugins.file_ui@really_delete')))
            return;

        widgetEm.find('input[value="' + uid + '"]').remove();
        widgetEm.append('<input type="hidden" name="' + widgetUid + '_to_delete" value="' + uid + '">');
        $(slot.remove());
        renumberSlots();

        --filesCount;
        addBtn.removeClass('hidden sr-only');
        widgetEm.removeClass('max-files-reached');

        sortableSetup();
    }

    function uploadFile(file) {
        if (acceptedFileTypes !== '*/*' && file.type.split('/')[0] !== acceptedFileTypes) {
            alert(lang.t('plugins.file_ui@file_has_invalid_type'));
            return false;
        }

        if (maxFileSize && file.size > maxFileSize) {
            alert(lang.t('plugins.file_ui@file_too_big', {
                file_name: file.name,
                max_size: maxFileSizeMB
            }));

            return false;
        }

        var formData = new FormData();
        formData.append(widgetUid, file);

        ++filesCount;

        if (filesCount === maxFiles)
            widgetEm.addClass('max-files-reached');

        if (filesCount > maxFiles) {
            filesCount = maxFiles;
            progressSlot.css('display', 'none');
            alert(lang.t('plugins.file_ui@max_files_exceeded'));

            return false;
        }

        $.ajax({
            type: 'POST',
            url: postUrl,
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function () {
                progressBar.css('width', '0');
                progressBar.attr('aria-valuenow', '0');
                progressBar.text('0%');
                progressSlot.css('display', 'flex');
                addBtn.css('display', 'none');

                $(widget).trigger('fileUploadStart');
            },
            xhr: function () {  // Custom XMLHttpRequest
                var myXhr = $.ajaxSettings.xhr();
                if (myXhr.upload) { // Check if upload property exists
                    myXhr.upload.addEventListener('progress', function (evt) {
                        var percentage = parseInt(evt.loaded / evt.total * 100);
                        progressBar.css('width', percentage + '%');
                        progressBar.attr('aria-valuenow', percentage);
                        progressBar.text(percentage + '%');
                    });
                }
                return myXhr;
            }
        }).done(function (data) {
            $.each(data, function (k, v) {
                var data = {
                    preview_image: previewImages,
                    thumb_width: thumbWidth,
                    thumb_height: thumbHeight,
                };

                httpApi.get('file' + '/' + v['uid'], data).then(r => {
                    progressSlot.css('display', 'none');
                    appendSlot(createSlot(r['uid'], r['url'], r['thumb_url'], r['name']));
                    $(widget).trigger('fileUploadSuccess', [v]);
                });
            });
        }).catch((jqXHR, textStatus, errorThrown) => {
            --filesCount;
            progressSlot.css('display', 'none');
            addBtn.css('display', 'flex');
            widgetEm.removeClass('max-files-reached');
            $(widget).trigger('fileUploadFail');
            alert(errorThrown);
        });
    }

    fileInput.change(function () {
        var files = this.files;

        $(widget).trigger('widgetChange');

        for (var i = 0; i < files.length; i++)
            uploadFile(files[i]);
    });

    // Open file select dialog
    widget.open = function () {
        $(widget).trigger('widgetOpen');
        fileInput[0].click();
    };

    // Remove all existing slots
    widget.clear = function (confirmDelete) {
        fileInput.val('');

        slotsEm.find('.slot-content').each(function () {
            removeSlot(this, confirmDelete);
        });

        $(widget).trigger('widgetClear');
    };

    // Initial setup of existing slots
    progressSlot.css('display', 'none');
    widgetEm.find('.slot').each(function () {
        setupSlot(this);
    });

    renumberSlots();
    sortableSetup();
});
