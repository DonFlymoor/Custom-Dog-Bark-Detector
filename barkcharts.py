import json, datetime, os
import matplotlib.pyplot as plt 
import pygame
from pygame import gfxdraw

# Initiate Pygame
pygame.init()


def load(file_name):
    '''
    Function to load data from JSON file
    '''
    try:
        # Try to load JSON data
        with open(file_name) as file:
            file_data = json.load(file)
        return file_data
    except Exception as error:
        print(f'Error loading data from {file_name}')
        return error

def graph(file_data):
    '''
    Display barks with a line graph
    '''

    # List of barks
    barks = []
    # Load barks into this format: 1 if bark within four second segment, zero if no bark 
    bark_chart = file_data['bark_chart']
    # Split the barks into one-minute segments
    array = splits(bark_chart, 15)

    # Change data to plottable data
    for bark_segment in array:
        bark_count = 0
        for _bark in bark_segment:
            bark_count+=int(_bark)
        barks+=[bark_count]
##    x=[]
##    j=0
##    for bark in bark_list:
##        while int(bark.split(':')[1]) - j > 1:
##            print(int(bark.split(':')[1]),j)
##            j+=1
##            barks+=[0]
##            x+=[str(j)]
##        try:
##            barks[i]+=1
##        except:
##            barks+=[1]
##            x+=[bark.split(':')[1]]
##
    # List of number of barks
    time=[i for i in range(len(barks))]
    # plotting the points  
    #plt.plot(x, y) 
    plt.plot(time, barks)  
    # naming the x axis 
    plt.xlabel('time') 
    # naming the y axis 
    plt.ylabel('barks') 
      
    # giving a title to my graph 
    plt.title(file_data['date']) 
      
    # function to show the plot 
    plt.show() 

def splits(data, length):
    '''
    Splits data into length-sized segments
    '''
    array = [data[i:i + length] for i in range(0, len(data), length)]
    return array

def plot(file_data):
    '''
    Print barks as *s
    '''
    bark_chart = file_data['bark_chart'].replace('_',' ').replace('O','*')
    bark_chart = splits(bark_chart,15)
    x=0
    for barks in bark_chart:
        if x == 4:
            print(" | "+barks+" | ")
            x=0
        else:
            print(" | "+barks+" | ",end='')
        x+=1
        
def pygame_plot(files):
    '''
    Visual representation of barks
    '''

    # Initiate font
    pygame.font.init()
    # Set font type and size
    Comic_Sans_MS_30 = pygame.font.SysFont('Comic Sans MS', 80)
    Comic_Sans_MS_10 = pygame.font.SysFont('Comic Sans MS', 40)
    
    height = int(3300)
    width = int(2550)
    canvas = pygame.display.set_mode([width, height])
    
    FILE_DATA = load('results/'+files[0])
    files_data = [file_data for file_data in [load('results/'+file) for file in files] if file_data['date'] == FILE_DATA['date']]
    date = Comic_Sans_MS_30.render(FILE_DATA['date'], False, (0, 0, 0))
    
    running = True
    size = 4
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        canvas.fill((255, 255, 255))

        canvas.blit(date,(int(width/2-100), int(-10)))

        for I in range(len(files_data)):
            file_data = files_data[I]
            bark_chart = file_data['bark_chart'].replace('_','0').replace('O','1')
            time = Comic_Sans_MS_10.render(file_data['time'].split('/')[0]+':'+file_data['time'].split('/')[1], False, (0, 0, 0))
            canvas.blit(time,(int(0), int(115+20*I)))
            
            for i in range(len(bark_chart)):
                
                x = int(i * size * 0.6)
                y = 150+20#*i

               
                
                while x > width-size*3:
                    x-=width-size*3
                    y+=size*4+5

                if y == 150:
                    x += 120

                if (i/(15*15)).is_integer():
                    pygame.draw.rect(canvas, (0, 0, 0), (x, y-(size*10)/2, 4, size*10))
                    
                if bark_chart[i] == '1':
                    draw_circle(canvas, x, y, size, (0, 0, 0))
        pygame.display.flip()
        break
    
    pygame.image.save(canvas, "results/"+files[0].replace('.json','.png'))
    
    pygame.quit()

def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)
    
def main():
    files = [file_name for file_name in os.listdir('results') if '.png' not in file_name]
    #files = ['bark.json']
    pygame_plot(files)
    '''
    for file in files:
        if '.json' not in file:
            continue
        print('file: '+file)
        data = load('results/'+file)
        pygame_plot(data, file)
    '''
if __name__ == '__main__':
    main()
