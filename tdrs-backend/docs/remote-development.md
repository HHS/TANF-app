# Remote Development

There will be times when a developer needs access to a container or a remote machine to debug a running application, or to change source code without needing to trigger a formal deployment. This document specifically describes how to use the Cloud.gov environments where TDRS is deployed as development environments.

## Tools

### Visual Studio Code
This guide presumes the use of [VS Code](https://code.visualstudio.com/) with the [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension pack. You can achieve a similar setup on other IDEs or in the terminal (as this all uses OpenSSH underneath); please save yourself the time and just go download VS Code.

### **`cf-cli`**
Additionally, install the latest version of the  [Cloudfoundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html) if you haven't.

## Access Cloudfoundry

Login to CloudFoundry with the CLI:

```shell
 cf login -a api.fr.cloud.gov  --sso
```

### Get App GUID

Use `curl` to get the process GUID of the application on deployed application you want to connect to; replace `<app-name>` with a string like `tdp-backend-raft`. You can see a list of currently running app names with `cf apps`.

```shell
cf curl /v3/apps/$(cf app <app-name> --guid)/processes | jq --raw-output '.resources | .[] | select(.type == "web").guid'
```

**This GUID will be used to construct the `User` name of the SSH connection.** 

## Create an SSH Config

Create a file `~/username/.ssh/config` if one doesn't exist, and append the Host setting below:

```
# Read more about SSH config files: https://linux.die.net/man/5/ssh_config
Host <app-name>
    HostName ssh.fr.cloud.gov
    User cf:<guid>/0
    Port 2222
```

Where `<guid>` is the string received in the last step. The User setting should look like this: `User cf:38f6a064-4ba7-4693-8732-960dea9f32f8/0`. Note the `/0` at the end of the string is the ID of the *instance*.

To connect with `ssh` from the terminal:

```shell
ssh -p 2222 cf:<guid>/0@ssh.fr.cloud.gov
```

## Get a One Time Password

In VS Code, open the command menu (ctrl/cmd+shift+p), type "Remote-SSH", and select "Connect Current Window to Host". This should automatically look at the previously created config, and now prompt you for a one time password.

```shell
cf ssh-code
```

## Navigate to Application Code

You should now be connected to the remote host, and need only navigate to the directory containing the application code you want to change (likely `/home/vcap/app/`).

Note that redeploying or restaging will wipe all changes made remotely.

## Useful Links

[VS Code Remote Overview](https://code.visualstudio.com/docs/remote/remote-overview)
[Jetbrains Remote development](https://www.jetbrains.com/help/idea/remote-development-starting-page.html)
