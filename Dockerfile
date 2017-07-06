FROM openjdk:8-jdk

# Create a work directory
RUN mkdir /tmp/work

# Just need to copy the library jar file over
COPY VirtualBot.jar /tmp/work
