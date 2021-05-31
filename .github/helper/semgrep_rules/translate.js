// ruleid: vmraid-translation-empty-string
__("")
// ruleid: vmraid-translation-empty-string
__('')

// ok: vmraid-translation-js-formatting
__('Welcome {0}, get started with ERPAdda in just a few clicks.', [full_name]);

// ruleid: vmraid-translation-js-formatting
__(`Welcome ${full_name}, get started with ERPAdda in just a few clicks.`);

// ok: vmraid-translation-js-formatting
__('This is fine');


// ok: vmraid-translation-trailing-spaces
__('This is fine');

// ruleid: vmraid-translation-trailing-spaces
__(' this is not ok ');
// ruleid: vmraid-translation-trailing-spaces
__('this is not ok ');
// ruleid: vmraid-translation-trailing-spaces
__(' this is not ok');

// ok: vmraid-translation-js-splitting
__('You have {0} subscribers in your mailing list.', [subscribers.length])

// todoruleid: vmraid-translation-js-splitting
__('You have') + subscribers.length + __('subscribers in your mailing list.')

// ruleid: vmraid-translation-js-splitting
__('You have' + 'subscribers in your mailing list.')

// ruleid: vmraid-translation-js-splitting
__('You have {0} subscribers' +
    'in your mailing list', [subscribers.length])

// ok: vmraid-translation-js-splitting
__("Ctrl+Enter to add comment")

// ruleid: vmraid-translation-js-splitting
__('You have {0} subscribers \
    in your mailing list', [subscribers.length])
