# Mail Setup

Grouprise supports the email protocol for different purposes:

* send notifications to users, which are subscribed to groups or communication threads
* receive incoming mails directed at a group or responding to a communication thread
  (similar to a mailinglist)

Mail notifications are enabled by default.
Processing of incoming emails needs to be configured (see below).


## Mail notifications

Outgoing email submission is configured in the [`email_submission`](configuration/options.html#email-delivery-of-outgoing-messages) configuration section.

The `From` address of outgoing mail is configurable:

* [`default_distinct_from_email`](configuration/options.html#default-distinct-from-email): one-way notifications
* [`default_reply_to_email`](configuration/options.html#default-reply-to-email): notifications, which can be answered


## Processing incoming emails

Incoming emails can be configured in different ways (or disabled).

See [grouprise options](/administration/configuration/options) for the specific settings mentioned below.


### Disable reception of emails

Mail reception is disabled by default.
It can be enabled by setting [`mailinglist_enabled`](configuration/options.html#mailinglist-enabled) to `true`.
In this case, all outgoing mails use [`default_distinct_from_email`](configuration/options.html#default-distinct-from-email) as their `From` address.
Users need to use the web-interface of *grouprise* for communication afterwards.


### LMTP

The preferred setup for mail delivery to *grouprise* is based on LMTP.
A minimal LMTP server is part of *grouprise*.
The server can be enabled by installing the [deb package](/deployment/deb) `grouprise-lmtpd` package
or by executing `grouprisectl run_lmtpd`.

All incoming mails are instantly handed over to *grouprise*.

The upstream mailserver (e.g. postfix) needs to be configured for delivering all mails for this
mail domain to the LMTP server of *grouprise*.


### Scripted processing

Most mail servers offer a ["dotforward"-style](https://www.courier-mta.org/dot-forward.html)
interface for delivering an incoming email via an executable.
Grouprise provides such an executable as `grouprisectl import_mail_message`.

This delivery method can be used in two ways:

* A) domain-global forwarding: Configure `| grouprisectl import_mail_message` as the mail delivery
     mechanism for all addresses of the mail domain.
* B) single inbox forwarding: Redirect all incoming mails for the domain into a single mailbox
     (see [`collector_mailbox_address`](configuration/options.html#collector-mailbox-address)).  Configure `| grouprisectl import_mail_message` as mail
     forwarding for this single mailbox.

Please note two disadvantages of the scripted processing in comparison to the LMTP service (above):

* The upstream mailserver cannot verify, whether a destination mail address is valid or not.
  Thus, it is forced to accept all incoming mail messages for this domain during the SMTP session.
  In case of a rejection by *grouprise*, this will cause subsequent
  [backscatter](https://en.wikipedia.org/wiki/Backscatter_%28email%29) (delivery failure emails).
  Early rejection during the initial SMTP session would be preferable (see *LMTP* above).
* Forwarding all mails to a single mailbox ([`collector_mailbox_address`](configuration/options.html#collector-mailbox-address)) breaks the proper handling
  of `CC` and `BCC` addressing.
