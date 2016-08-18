# irssi-notify.pl
use Irssi;
use Net::DBus;
use Switch;

$::VERSION='0.0.1';
%::IRSSI = (
    authors => 'Ashish Shukla',
    contact => 'gmail.com!wahjava',
    name => 'irssi-notify',
    description => 'Displays a pop-up message for message received',
    url => 'http://wahjava.wordpress.com/',
    license => 'GNU General Public License',
    changed => '$Date$'
    );

my $APPNAME = 'Irssi';
my $MAXLEN = 10;
my $TERMNAME = 'urxvtc';
my $SND_PRV_MSG = '/home/alex/.irssi/receive.wav';
my $SND_PRES_ON = '/home/alex/.irssi/login.wav';
my $SND_PRES_OFF = '/home/alex/.irssi/logout.wav';

my $IMG_IRC = '/home/alex/.irssi/irc.svg';
my $IMG_XMPP = '/home/alex/.irssi/jabber.svg';

my $IMG_LOGIN = '/home/alex/.irssi/log-in.png';
my $IMG_LOGOUT = '/home/alex/.irssi/log-out.png';

my $IMG_AVAILABLE = '/home/alex/.irssi/available.png';
my $IMG_AWAY = '/home/alex/.irssi/away.png';
my $IMG_EXTENDED_AWAY = '/home/alex/.irssi/na.png';
my $IMG_DND = '/home/alex/.irssi/dnd.png';
my $IMG_FFC = '/home/alex/.irssi/chat.png';
my $IMG_OFFLINE = '/home/alex/.irssi/offline.png';

my $bus = Net::DBus->session;
my $notifications = $bus->get_service('org.freedesktop.Notifications');
my $object = $notifications->get_object('/org/freedesktop/Notifications',
					'org.freedesktop.Notifications');
					
my $cmd_notify_sound = 0;
my $cmd_notify_focus = 0;
my $cmd_notify_img = 0;

# $object->Notify('appname', 0, 'info', 'Title', 'Message', [], { }, 3000);

sub trunstr {
	my ($str, $len) = @_;

	if (length($str) <= $len) {
		return $str;
	} else {
		return substr($str, 0, $len);
	}
}

sub client_has_focus {
	my $output = qx/xdotool getwindowname `xdotool getwindowfocus`/;
	
	if ($output =~ $APPNAME) {
		return 0;
	} else {
		return 0;
	}
}

sub im_image {
	my ($server) = @_;

	if (!$cmd_notify_img) {
		return '';
	}
	
	if ($server->{chat_type} =~ 'IRC') {
		return $IMG_IRC;
	} elsif ($server->{chat_type} =~ 'XMPP') {
		return $IMG_XMPP;
	} else {
		return $IMG_IRC;
	}
}

# appname, id, icon, summary, body, ...
sub notify {
	my ($name, $icon, $title, $message, $duration) = @_;
	
	$object->Notify($name, 0, $icon, $title, $message, [], { }, $duration);
}

sub play_sound {
	my ($file) = @_;

	if (!$cmd_notify_sound) {
		return;
	}
	
	system("aplay \"$file\" > /dev/null 2>&1 &");
}

sub pub_msg {
    my ($server, $msg, $nick, $address, $target) = @_;

    if ($msg =~ $server->{nick})
    {
		if(client_has_focus()) {
			return;
		}
		
		play_sound($SND_PRV_MSG);
		
		my $tnick = trunstr($nick, $MAXLEN);
		
		notify("${APPNAME}", im_image($server), "Public Message in $target", "$tnick: $msg", 0);
    }
}

sub priv_msg {
    my ($server, $msg, $nick, $address) = @_;
    
    if (client_has_focus()) {
		return;
	}
	
	my $type = $server->{chat_type};
    
	play_sound($SND_PRV_MSG);
    
	my $tnick = trunstr($nick, $MAXLEN);
	
	notify("${APPNAME}", im_image($server), 'Private Message', "$tnick: $msg", 0);
}

Irssi::signal_add_last('message public', \&pub_msg);
Irssi::signal_add_last('message private', \&priv_msg);

